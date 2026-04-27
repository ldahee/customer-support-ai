from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.synthesizer.synthesizer_prompt import synthesizer_prompt
from app.schemas.expert_output import ExpertOutput


def build_synthesizer():
    llm = ChatOpenAI(
        model=settings.synthesizer_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0.2,
    )
    return synthesizer_prompt | llm.with_structured_output(ExpertOutput)


synthesizer_chain = build_synthesizer()
