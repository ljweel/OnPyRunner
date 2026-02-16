# app.py
from fastapi import FastAPI, HTTPException
from models.request import ExecuteRequest
from models.payload import JobExecutionPayload
from models.response import JobResponse, PendingJobResponse
from models.common import Limits
import uuid, json
import redis

app = FastAPI()

redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

if redis_client.ping():
    print("Redis connected to app")
else:
    print("Redis not connected to app")


@app.post("/execute", response_model=PendingJobResponse)
async def execute(request: ExecuteRequest):
    # create job id
    job_id = str(uuid.uuid4())
    # create execution payload
    execution_payload = JobExecutionPayload(
        job_id=job_id,
        language=request.language,
        source_code=request.source_code,
        stdin=request.stdin or "",
        limits=request.limits or Limits()
    )
    # enqueue job to redis queue
    redis_client.lpush(
        "queue:job_queue",  # queue name
        execution_payload.model_dump_json()  # payload to json
    )

    # create job response
    pending_job_response = PendingJobResponse(job_id=job_id)

    # save job status in redis
    redis_client.set(
        f"job:{job_id}",  # job key
        pending_job_response.model_dump_json()  # response to json
    )
    return pending_job_response


@app.get("/jobs/{job_id}", response_model=JobResponse, response_model_exclude_none=True)
async def get_job(job_id: str):

    # get job from redis
    job_data = redis_client.get(f"job:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(job_data)