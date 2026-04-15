import json
import uuid
from datetime import datetime, timezone
from typing import cast

import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from onpyrunner_db.service import create_execution, update_execution
from onpyrunner_shared.logger import setup
from onpyrunner_shared.models.payload import JobExecutionPayload
from onpyrunner_shared.models.request import ExecuteRequest
from onpyrunner_shared.models.response import JobResponse, PendingJobResponse

app = FastAPI()

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://run.ljweel.dev",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

if redis_client.ping():
    print("Redis connected to app")
else:
    print("Redis not connected to app")


log = setup("api_server")


@app.post("/execute", response_model=PendingJobResponse)
async def execute(request: ExecuteRequest):

    api_received_at = datetime.now(timezone.utc)

    # create job id
    job_id = str(uuid.uuid4())
    log.info("job created", extra={"jobId": job_id})
    await create_execution(
        job_id=job_id,
        language=request.language,
        source_code=request.source_code,
        stdin=request.stdin or "",
    )

    # create execution payload
    execution_payload = JobExecutionPayload(
        job_id=job_id,
        language=request.language,
        source_code=request.source_code,
        stdin=request.stdin or "",
    )

    queue_entered_at = datetime.now(timezone.utc)

    # enqueue job to redis queue
    redis_client.lpush(
        "queue:job_queue",  # queue name
        execution_payload.model_dump_json(),  # payload to json
    )

    # create job response
    pending_job_response = PendingJobResponse(job_id=job_id)

    # save job status in redis
    redis_client.set(
        f"job:{job_id}",  # job key
        pending_job_response.model_dump_json(),  # response to json
        ex=600,  # expire in 10 minutes
    )

    log.info("job enqueued", extra={"jobId": job_id})
    await update_execution(
        job_id=job_id,
        api_received_at=api_received_at,
        queue_entered_at=queue_entered_at,
    )
    return pending_job_response


@app.get("/jobs/{job_id}", response_model=JobResponse, response_model_exclude_none=True)
async def get_job(job_id: str):

    # get job from redis
    job_data = cast(str | None, redis_client.get(f"job:{job_id}"))
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(job_data)
