from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.experts.shipping_prompt import shipping_prompt
from app.schemas.expert_output import ExpertOutput

shipping_chain = shipping_prompt | ChatOpenAI(
    model=settings.shipping_model,
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url or None,
    temperature=0.2,
).with_structured_output(ExpertOutput)
