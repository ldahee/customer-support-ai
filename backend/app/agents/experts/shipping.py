from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.experts.shipping_prompt import shipping_prompt
from app.schemas.expert_output import ExpertOutput


def build_shipping_agent() -> object:
    llm = ChatOpenAI(
        model=settings.shipping_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(ExpertOutput)
    return shipping_prompt | structured_llm


shipping_chain = build_shipping_agent()
