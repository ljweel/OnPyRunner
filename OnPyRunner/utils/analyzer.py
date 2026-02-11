from nsjail.result import NsJailResult
from models.common  import JobResult, JobStatus, JobOutcome
from models.response import JobResponse
from models.response import CompletedJobResponse



class ResultAnalyzer:
    def _result_to_outcome(self, raw_result: NsJailResult) -> JobOutcome:

        exit_code = raw_result.exit_code
        if exit_code == 0:
            return JobOutcome.SUCCESS
        if exit_code == 1:
            return JobOutcome.RUNTIME_ERROR
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
                usage_info=raw_result.usage_info
            )
        )