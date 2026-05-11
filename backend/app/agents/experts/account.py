from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.experts.account_prompt import account_prompt
from app.schemas.expert_output import ExpertOutput

account_chain = account_prompt | ChatOpenAI(
    model=settings.account_model,
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url or None,
    temperature=0.2,
).with_structured_output(ExpertOutput)
