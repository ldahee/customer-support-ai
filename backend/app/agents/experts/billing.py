from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.experts.billing_prompt import billing_prompt
from app.schemas.expert_output import ExpertOutput

billing_chain = billing_prompt | ChatOpenAI(
    model=settings.billing_model,
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url or None,
    temperature=0.2,
).with_structured_output(ExpertOutput)
