from typing import Literal
from pydantic import BaseModel, Field

VALID_CATEGORIES = Literal["billing", "account", "technical_support", "shipping", "general"]


class RouterOutput(BaseModel):
    category: VALID_CATEGORIES = Field(
        description="문의가 속하는 카테고리. billing/account/technical_support/shipping/general 중 하나."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="분류 신뢰도. 0.0~1.0 사이의 수치."
    )
    routing_reason: str = Field(
        description="해당 카테고리로 분류한 근거."
    )
