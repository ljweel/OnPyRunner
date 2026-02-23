# models/request.py
from pydantic import BaseModel, Field, field_validator
from models.common import Language

MAX_LENGTH = 100000

# POST /execute request body model
class ExecuteRequest(BaseModel):
    language: Language = Field(..., description="언어")
    source_code: str = Field(..., description="소스 코드")
    stdin: str|None = Field(default=None, description="표준 입력")



    @field_validator("source_code")
    def check_source_size(cls, v):
        if len(v.encode("utf-8")) > MAX_LENGTH:
            raise ValueError("source code exceeds 10KB.")
        return v

    @field_validator("stdin")
    def check_stdin_size(cls, v):
        if v is not None and len(v.encode("utf-8")) > MAX_LENGTH:
            raise ValueError("stdin exceeds 10KB.")
        return v

