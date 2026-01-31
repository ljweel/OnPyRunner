# models/request.py
from pydantic import BaseModel, Field
from models.common import Limits

# POST /execute request body model
class ExecuteRequest(BaseModel):
    language: str = Field(..., description="언어")
    source_code: str = Field(..., description="소스 코드")
    stdin: str|None = Field(default=None, description="표준 입력")
    limits: Limits|None = Field(default=None, description="작업 제한 사항")
