import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta, timezone

import redis.asyncio as aioredis
from onpyrunner_db.service import update_execution
from onpyrunner_shared.logger import setup
from onpyrunner_shared.models.response import FailedJobResponse, RunningJobResponse
from redis.asyncio import Redis

from onpyrunner_worker.analyzer import ResultAnalyzer
from onpyrunner_worker.nsjail import NsJail
from onpyrunner_worker.nsjail.result import NsJailResult


async def worker_init(redis_client: Redis):
    if await redis_client.ping():  # type: ignore
        print("Redis connected to worker")
    else:
        print("Redis not connected to worker")


def run_sandboxed_task(job_id: str, source_code: str, stdin: str) -> NsJailResult:
    runner = NsJail(job_id)
    return runner.execute(source_code, stdin)


async def worker_loop(redis_client: Redis, log: logging.Logger):
    while True:
        result = await redis_client.brpop("queue:job_queue", timeout=0)  # type: ignore

        _, execution_payload = result  # type: ignore
        execution_payload_dict = json.loads(execution_payload)
        job_id = execution_payload_dict["job_id"]
        source_code = execution_payload_dict["source_code"]
        stdin = execution_payload_dict["stdin"]

        await update_execution(
            job_id=job_id,
            worker_picked_at=datetime.now(timezone(timedelta(hours=9))),
            status="RUNNING",
        )

        log.info("job dequeued", extra={"jobId": job_id})

        running_job_response = RunningJobResponse(job_id=job_id)

        # save job status in redis
        await redis_client.set(
            f"job:{job_id}",  # job key
            running_job_response.model_dump_json(),  # response to json
            ex=600,  # expire in 10 minutes
        )

        try:
            log.info("sandbox start", extra={"jobId": job_id})

            await update_execution(
                job_id=job_id,
                execution_started_at=datetime.now(timezone(timedelta(hours=9))),
            )

            nsjail_result = run_sandboxed_task(job_id, source_code, stdin)

            await update_execution(
                job_id=job_id,
                execution_finished_at=datetime.now(timezone(timedelta(hours=9))),
            )
        except Exception as e:
            # infrastructure error
            failed_job_response = FailedJobResponse(job_id=job_id, reason=str(e))

            await redis_client.set(
                f"job:{job_id}",
                failed_job_response.model_dump_json(),
                ex=600,
            )

            await update_execution(
                job_id=job_id,
                status="FAILED",
                fail_reason=failed_job_response.reason,
            )

            sys.exit(1)
        finally:
            log.info("sandbox end", extra={"jobId": job_id})

        completed_job_response = ResultAnalyzer().analyze(job_id, nsjail_result)

        await redis_client.set(
            f"job:{job_id}",
            completed_job_response.model_dump_json(),
            ex=600,
        )
        log.info("result analysed", extra={"jobId": job_id})

        await update_execution(
            job_id=job_id,
            result_stored_at=datetime.now(timezone(timedelta(hours=9))),
            status="COMPLETED",
            outcome=completed_job_response.result.outcome,
            stdout=completed_job_response.result.stdout,
            stderr=completed_job_response.result.stderr,
            exit_code=completed_job_response.result.exit_code,
            cpu_time_ms=completed_job_response.result.usage_info.cpu_time_ms,
            wall_time_ms=completed_job_response.result.usage_info.wall_time_ms,
        )


async def main():
    redis_client = aioredis.from_url("redis://redis:6379/0", decode_responses=True)
    log = setup("worker")

    await worker_init(redis_client)
    await worker_loop(redis_client, log)


if __name__ == "__main__":
    asyncio.run(main())
