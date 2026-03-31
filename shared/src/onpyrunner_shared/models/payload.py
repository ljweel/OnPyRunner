from pydantic import BaseModel, Field

from onpyrunner_shared.models.common import Language


class JobExecutionPayload(BaseModel):
    job_id: str = Field(..., description="작업 ID")
    language: Language = Field(..., description="언어")
    source_code: str = Field(..., description="소스 코드")
    stdin: str | None = Field(default=None, description="표준 입력")
