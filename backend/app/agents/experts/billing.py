import logging

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.prompts.experts.billing_prompt import BILLING_SYSTEM, billing_prompt
from app.schemas.expert_output import ExpertOutput

logger = logging.getLogger(__name__)


async def _fetch_billing_mcp_context(inquiry_text: str) -> str:
    from app.mcp.client import mcp_manager  # 순환 임포트 방지

    tools = mcp_manager.get_tools_for_expert("billing")
    if not tools:
        return ""

    parts = []
    for tool in tools:
        try:
            result = await tool.ainvoke({"query": inquiry_text})
            if result:
                parts.append(f"[{tool.name}]\n{result}")
        except Exception as e:
            logger.debug("MCP tool '%s' skipped: %s", tool.name, e)

    return "\n\n".join(parts)


def _build_billing_prompt(mcp_context: str) -> ChatPromptTemplate:
    if not mcp_context:
        return billing_prompt

    system = BILLING_SYSTEM + f"""

## 실시간 조회 데이터
다음은 고객의 결제 관련 실시간 데이터입니다. 이를 바탕으로 정확한 답변을 제공하세요:

{mcp_context}
"""
    return ChatPromptTemplate.from_messages([
        ("system", system),
        MessagesPlaceholder("chat_history"),
        ("human", "다음 결제 관련 문의에 답변해주세요:\n\n<customer_inquiry>\n{inquiry_text}\n</customer_inquiry>"),
    ])


def build_billing_agent() -> RunnableLambda:
    llm = ChatOpenAI(
        model=settings.billing_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(ExpertOutput)

    async def _invoke(inputs: dict) -> ExpertOutput:
        mcp_context = await _fetch_billing_mcp_context(inputs.get("inquiry_text", ""))
        if mcp_context:
            logger.info("billing_expert: MCP context injected (%d chars)", len(mcp_context))
        prompt = _build_billing_prompt(mcp_context)
        return await (prompt | structured_llm).ainvoke(inputs)

    return RunnableLambda(_invoke)


billing_chain = build_billing_agent()
