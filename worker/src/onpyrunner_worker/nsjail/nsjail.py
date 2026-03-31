import resource
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import IO, Iterable, Sequence

from onpyrunner_shared.models.common import UsageInfo
from onpyrunner_shared.logger import setup
from onpyrunner_worker.nsjail.result import NsJailResult

log = setup("nsjail")

MAX_STDOUT_SIZE = 128 * 1024  # 128KB
MAX_STDERR_SIZE = 128 * 1024  # 128KB

CFG_PATH = Path(__file__).parent / "nsjail.cfg"


class NsJail:
    def __init__(self, job_id: str):
        self.config_path: Path = CFG_PATH
        self.nsjail_path: Path = Path("/usr/bin/nsjail")
        self.base_sandbox_dir: Path = Path("/sandbox")
        self.python_path: Path = Path("/usr/local/bin/python3")
        self.job_id: str = job_id

    def _write_files(self, code_file: str, stdin: str) -> Iterable[Path]:
        sandbox_dir = self.base_sandbox_dir / self.job_id
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        code_path = sandbox_dir / "main.py"
        stdin_path = sandbox_dir / "stdin.txt"
        with open(code_path, "w") as f:
            f.write(code_file)
        with open(stdin_path, "w") as f:
            f.write(stdin)
        return code_path, stdin_path

    def _consume_stream(
        self, proc: subprocess.Popen, stream: IO[bytes] | None, max_size: int
    ) -> tuple[str, bool]:
        if stream is None:
            raise RuntimeError("Stream is None")
        output = []
        output_size = 0
        is_output_exceeded = False
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            output_size += len(chunk)
            output.append(chunk)
            if output_size > max_size:
                proc.terminate()
                is_output_exceeded = True
                break
        return (
            b"".join(output)[:max_size].decode("utf-8", errors="replace"),
            is_output_exceeded,
        )

    def _build_command(self, code_path: Path) -> Sequence[str | Path]:
        return [
            self.nsjail_path,
            "--config",
            self.config_path,
            "-q",
            "--",
            self.python_path,
            code_path,
        ]

    def _run(self, code_path: Path, stdin_path: Path) -> NsJailResult:
        cmd = self._build_command(code_path)
        with stdin_path.open("r") as f:
            start_wall_time = time.perf_counter()
            start_cpu_time = resource.getrusage(resource.RUSAGE_CHILDREN)

            log.info("usercode start", extra={"jobId": self.job_id})
            result = subprocess.Popen(
                cmd, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            with ThreadPoolExecutor(max_workers=2) as executor:
                stdout_future = executor.submit(
                    self._consume_stream, result, result.stdout, MAX_STDOUT_SIZE
                )
                stderr_future = executor.submit(
                    self._consume_stream, result, result.stderr, MAX_STDERR_SIZE
                )
                stdout, stdout_exceeded = stdout_future.result()
                stderr, stderr_exceeded = stderr_future.result()
            result.wait(timeout=6)

            log.info("usercode end", extra={"jobId": self.job_id})

            end_wall_time = time.perf_counter()
            end_cpu_time = resource.getrusage(resource.RUSAGE_CHILDREN)

            wall_time_ms = int((end_wall_time - start_wall_time) * 1000)
            cpu_time_ms = int(
                (
                    (end_cpu_time.ru_utime + end_cpu_time.ru_stime)
                    - (start_cpu_time.ru_utime + start_cpu_time.ru_stime)
                )
                * 1000
            )
            usage_info = UsageInfo(cpu_time_ms=cpu_time_ms, wall_time_ms=wall_time_ms)

        return NsJailResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=result.returncode,
            usage_info=usage_info,
            stdout_exceeded=stdout_exceeded,
            stderr_exceeded=stderr_exceeded,
        )

    def _cleanup(self):
        shutil.rmtree(self.base_sandbox_dir / self.job_id, ignore_errors=True)

    def execute(self, code_file: str, stdin: str) -> NsJailResult:
        try:
            code_path, stdin_path = self._write_files(code_file, stdin)
            result = self._run(code_path, stdin_path)
            return result
        except Exception as e:
            print(f"[Job {self.job_id}] Execution failed: {e}")
            raise e
        finally:
            self._cleanup()
