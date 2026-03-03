import json

import redis

from models.response import FailedJobResponse, RunningJobResponse
from nsjail.nsjail import NsJail
from nsjail.result import NsJailResult
from OnPyRunner.logging.init import setup
from OnPyRunner.utils.analyzer import ResultAnalyzer

redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

if redis_client.ping():
    print("Redis connected to worker")
else:
    print("Redis not connected to worker")

log = setup("worker")


def run_sandboxed_task(job_id: str, source_code: str, stdin: str) -> NsJailResult:
    runner = NsJail(job_id)
    return runner.execute(source_code, stdin)


def worker_loop():
    while True:
        result = redis_client.brpop("queue:job_queue", timeout=0)  # type: ignore
        _, execution_payload = result  # type: ignore
        execution_payload_dict = json.loads(execution_payload)
        job_id = execution_payload_dict["job_id"]
        source_code = execution_payload_dict["source_code"]
        stdin = execution_payload_dict["stdin"]

        log.info("job dequeued", extra={"jobId": job_id})

        running_job_response = RunningJobResponse(job_id=job_id)
        # save job status in redis
        redis_client.set(
            f"job:{job_id}",  # job key
            running_job_response.model_dump_json(),  # response to json
        )
        try:
            log.info("sandbox start", extra={"jobId": job_id})
            nsjail_result = run_sandboxed_task(job_id, source_code, stdin)
        except Exception as e:
            # infrastructure error
            failed_job_response = FailedJobResponse(job_id=job_id, reason=str(e))
            redis_client.set(f"job:{job_id}", failed_job_response.model_dump_json())
            exit(f"Failed to execute job{job_id}: {e}")
        finally:
            log.info("sandbox end", extra={"jobId": job_id})

        completed_job_response = ResultAnalyzer().analyze(job_id, nsjail_result)

        redis_client.set(f"job:{job_id}", completed_job_response.model_dump_json())
        log.info("result analysed", extra={"jobId": job_id})


if __name__ == "__main__":
    worker_loop()
