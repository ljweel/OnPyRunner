## Execution Architecture

OnPyRunner는 코드 실행을 HTTP 요청으로부터 분리된 Job 단위로 다룬다.
실제 코드는 nsjail 기반의 샌드박스 내부에서 실행되며,
이 역할을 담당하는 핵심 컴포넌트가 `NsJail` 클래스다.

+-----------------------------------------------------------------------+
|                                NsJail                                 |
+-----------------------------------------------------------------------+
| - job_id: str                                                         |
| - config_path: Path                                                   |
| - nsjail_path: Path                                                   |
| - base_sandbox_dir: Path                                              |
| - python_path: Path                                                   |
+-----------------------------------------------------------------------+
| + execute(code_file: str, input_file: str) -> NsJailResult            |
|-----------------------------------------------------------------------|
| [Internal Helpers - Private]                                          |
| - _write_files(code, input) -> Iterable[Path]                         |
| - _build_command(code_path) -> Sequence[str]                          |
| - _run(code_path, input_path) -> NsJailResult                         |
| - _cleanup() -> None                                                  |
+-----------------------------------------------------------------------+