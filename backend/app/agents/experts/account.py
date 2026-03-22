from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.experts.account_prompt import account_prompt
from app.schemas.expert_output import ExpertOutput


def build_account_agent() -> object:
    llm = ChatOpenAI(
        model=settings.account_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(ExpertOutput)
    return account_prompt | structured_llm


account_chain = build_account_agent()
