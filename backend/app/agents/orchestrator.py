from langchain_openai import ChatOpenAI

from app.agents.expert_tools import EXPERT_TOOLS
from app.config.settings import settings


def build_orchestrator_llm():
    llm = ChatOpenAI(
        model=settings.orchestrator_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0,
    )
    return llm.bind_tools(EXPERT_TOOLS)


orchestrator_llm = build_orchestrator_llm()
