import logging
from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.router.router_prompt import router_prompt
from app.schemas.router_output import RouterOutput

logger = logging.getLogger(__name__)


def build_router_agent() -> object:
    """Router Agent 체인을 빌드하여 반환합니다."""
    llm = ChatOpenAI(
        model=settings.router_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0,
    )
    structured_llm = llm.with_structured_output(RouterOutput)
    chain = router_prompt | structured_llm
    return chain


router_chain = build_router_agent()
