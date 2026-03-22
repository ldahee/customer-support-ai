from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.experts.technical_support_prompt import technical_support_prompt
from app.schemas.expert_output import ExpertOutput


def build_technical_support_agent() -> object:
    llm = ChatOpenAI(
        model=settings.technical_support_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(ExpertOutput)
    return technical_support_prompt | structured_llm


technical_support_chain = build_technical_support_agent()
