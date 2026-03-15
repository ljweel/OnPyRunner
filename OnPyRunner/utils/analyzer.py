from models.common import JobOutcome, JobResult, JobStatus
from models.response import CompletedJobResponse, JobResponse
from nsjail.result import NsJailResult


class ResultAnalyzer:
    def _result_to_outcome(self, raw_result: NsJailResult) -> JobOutcome:

        exit_code = raw_result.exit_code
        stderr = raw_result.stderr
        if exit_code == 0:
            return JobOutcome.SUCCESS
        elif exit_code == 1:
            if "MemoryError" in stderr:
                return JobOutcome.MEMORY_LIMIT_EXCEEDED
            else:
                return JobOutcome.RUNTIME_ERROR
        # 137(SIGKILL): nsjail 설정상 fork/파일I/O가 제한되어
        # cgroup OOM Kill 가능성이 낮으므로 TLE로 판정
        elif exit_code == 137:
            return JobOutcome.TIME_LIMIT_EXCEEDED
        else:
            return JobOutcome.UNKNOWN_ERROR

    def analyze(self, job_id: str, raw_result: NsJailResult) -> JobResponse:

        return CompletedJobResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            result=JobResult(
                outcome=self._result_to_outcome(raw_result),
                stdout=raw_result.stdout,
                stderr=raw_result.stderr,
                exit_code=raw_result.exit_code,
                usage_info=raw_result.usage_info,
            ),
        )
