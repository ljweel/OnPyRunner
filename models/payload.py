# models/payload.py
from pydantic import BaseModel, Field
from models.common import Language

# Job Execution Payload
class JobExecutionPayload(BaseModel):
    job_id: str = Field(..., description="작업 ID")
    language: Language = Field(..., description="언어")
    source_code: str = Field(..., description="소스 코드")
    stdin: str|None = Field(default=None, description="표준 입력")