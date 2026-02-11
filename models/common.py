# models/common.py
from __future__ import annotations
from pydantic import BaseModel, Field
from enum import Enum

# 작업 시간/메모리 제한
class Limits(BaseModel):
    cpu_time_ms: int = Field(default=3000, ge=100, le=3000, description="CPU 시간 제한 (ms) 최소 100ms, 최대 3000ms")
    memory_mb: int = Field(default=128, ge=1, le=128, description="메모리 제한 (MB) 최소 1MB, 최대 128MB")

# 작업 상태
class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# 작업 기본 모델
class JobBase(BaseModel):
    job_id: str = Field(..., description="작업 ID")
    status: JobStatus = Field(..., description="작업 상태")

# 작업 결과 모델
class JobResult(BaseModel):
    outcome: JobOutcome = Field(..., description="작업 결과")
    stdout: str = Field(..., description="표준 출력")
    stderr: str = Field(..., description="표준 에러")
    exit_code: int = Field(..., description="종료 코드")
    usage_info: UsageInfo = Field(..., description="사용 정보")

# 사용 정보 모델
class UsageInfo(BaseModel):
    cpu_time_ms: int = Field(..., description="CPU 사용 시간 (ms)")
    wall_time_ms: int = Field(..., description="총 실행 시간 (ms)")


class JobOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
