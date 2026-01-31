# models/response.py
from pydantic import Field
from typing import Literal, Union
from models.common import JobStatus, JobBase, JobResult


class PendingJobResponse(JobBase):
    status: Literal[JobStatus.PENDING] = JobStatus.PENDING

class RunningJobResponse(JobBase):
    status: Literal[JobStatus.RUNNING] = JobStatus.RUNNING

class CompletedJobResponse(JobBase):
    status: Literal[JobStatus.COMPLETED] = JobStatus.COMPLETED
    result: JobResult = Field(..., description="작업 결과")

class FailedJobResponse(JobBase):
    status: Literal[JobStatus.FAILED] = JobStatus.FAILED
    reason: str = Field(..., description="실패 사유")

JobResponse = Union[
    PendingJobResponse,
    RunningJobResponse, 
    CompletedJobResponse,
    FailedJobResponse
]