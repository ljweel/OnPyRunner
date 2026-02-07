import subprocess, shutil
from pathlib import Path
from typing import Sequence, Iterable
from models.common import UsageInfo
import time, resource
from nsjail.result import NsJailResult


class NsJail:
    def __init__(self, job_id: str):
        self.config_path: Path = "/app/nsjail/nsjail.cfg"
        self.nsjail_path: Path = "/usr/bin/nsjail"
        self.base_sandbox_dir: Path = Path("/sandbox")
        self.python_path: Path = "/usr/local/bin/python3"
        self.job_id: str = job_id
    
    def _write_files(self, code_file: str, stdin: str) -> Iterable[str]:
        sandbox_dir = self.base_sandbox_dir / self.job_id
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        code_path = sandbox_dir / "main.py"
        stdin_path = sandbox_dir / "stdin.txt"
        with open(code_path, "w") as f:
            f.write(code_file)
        with open(stdin_path, "w") as f:
            f.write(stdin)
        return code_path, stdin_path
    
    def _build_command(self, code_path: Path) -> Sequence[str]:
        return [
            self.nsjail_path,
            "--config", self.config_path,
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

            result = subprocess.run(
                cmd,
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout = 6,
            )

            end_wall_time = time.perf_counter()
            end_cpu_time = resource.getrusage(resource.RUSAGE_CHILDREN)

            wall_time_ms = int((end_wall_time - start_wall_time) * 1000)
            cpu_time_ms = int(((end_cpu_time.ru_utime + end_cpu_time.ru_stime) \
                        - (start_cpu_time.ru_utime + start_cpu_time.ru_stime)) * 1000)
            usage_info = UsageInfo(cpu_time_ms=cpu_time_ms, wall_time_ms=wall_time_ms)

        return NsJailResult(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
            usage_info=usage_info,
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