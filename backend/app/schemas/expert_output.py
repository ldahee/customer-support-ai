from typing import Literal, Optional
from pydantic import BaseModel, Field


class SafetyOutput(BaseModel):
    is_safe: bool = Field(description="요청이 정책 위반 또는 유해 여부. True이면 안전, False이면 차단.")
    reason: Optional[str] = Field(default=None, description="판단 근거.")


class ExpertOutput(BaseModel):
    answer: str = Field(description="사용자에게 전달할 최종 답변.")
    answer_type: Optional[Literal["direct", "guidance", "escalation_needed"]] = Field(
        default="direct",
        description="답변 유형."
    )
    escalation_needed: Optional[bool] = Field(
        default=False,
        description="사람 상담원 이관이 필요한 경우 True."
    )
