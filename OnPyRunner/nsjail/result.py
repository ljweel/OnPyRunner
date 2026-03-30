from pydantic import BaseModel, Field

from OnPyRunner.models.common import UsageInfo


class NsJailResult(BaseModel):
    stdout: str = Field(..., description="표준 출력")
    stderr: str = Field(..., description="표준 에러")
    exit_code: int = Field(..., description="종료 코드")
    usage_info: UsageInfo = Field(..., description="사용 정보")
    stdout_exceeded: bool = Field(..., description="표준 출력 초과 여부")
    stderr_exceeded: bool = Field(..., description="표준 에러 초과 여부")
