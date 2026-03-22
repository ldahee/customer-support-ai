import logging
from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.safety.safety_prompt import safety_prompt
from app.schemas.expert_output import SafetyOutput

logger = logging.getLogger(__name__)

SAFETY_BLOCKED_RESPONSE = (
    "죄송합니다. 해당 문의는 정책상 처리가 어렵습니다. "
    "서비스 이용 정책에 위반되는 요청이거나 처리 범위를 벗어난 요청입니다. "
    "일반적인 서비스 이용 관련 문의로 다시 접수해 주시기 바랍니다."
)


def build_safety_agent() -> object:
    """Safety Agent 체인을 빌드하여 반환합니다."""
    llm = ChatOpenAI(
        model=settings.safety_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0,
    )
    structured_llm = llm.with_structured_output(SafetyOutput)
    chain = safety_prompt | structured_llm
    return chain


safety_chain = build_safety_agent()
