import logging
from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.fallback.fallback_prompt import fallback_prompt
from app.schemas.expert_output import ExpertOutput

logger = logging.getLogger(__name__)


def build_fallback_agent() -> object:
    """Fallback Agent 체인을 빌드하여 반환합니다."""
    llm = ChatOpenAI(
        model=settings.fallback_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(ExpertOutput)
    chain = fallback_prompt | structured_llm
    return chain


fallback_chain = build_fallback_agent()
