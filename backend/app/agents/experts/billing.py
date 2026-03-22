from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.experts.billing_prompt import billing_prompt
from app.schemas.expert_output import ExpertOutput


def build_billing_agent() -> object:
    llm = ChatOpenAI(
        model=settings.billing_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(ExpertOutput)
    return billing_prompt | structured_llm


billing_chain = build_billing_agent()
