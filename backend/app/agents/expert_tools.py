"""
Expert Agent 체인을 LangChain tool로 노출합니다.
orchestrator_node에서 LLM의 tool 선택 결정에 사용되며,
실제 체인 실행은 노드 내부에서 TOOL_CHAIN_MAP을 통해 직접 수행합니다.
"""
from langchain_core.tools import tool

from app.agents.experts.billing import billing_chain
from app.agents.experts.account import account_chain
from app.agents.experts.technical_support import technical_support_chain
from app.agents.experts.shipping import shipping_chain


@tool
def billing_expert(inquiry_text: str) -> str:
    """결제, 청구, 환불, 결제 수단, 청구 오류 관련 문의를 처리합니다."""
    ...


@tool
def account_expert(inquiry_text: str) -> str:
    """계정 로그인, 비밀번호, 계정 잠금, 2FA, 계정 접근 관련 문의를 처리합니다."""
    ...


@tool
def technical_support_expert(inquiry_text: str) -> str:
    """앱/웹 오류, 기능 오작동, 접속 장애, 버그 신고 관련 문의를 처리합니다."""
    ...


@tool
def shipping_expert(inquiry_text: str) -> str:
    """배송 상태, 주문 추적, 배송 지연, 배송지 변경 관련 문의를 처리합니다."""
    ...


EXPERT_TOOLS = [billing_expert, account_expert, technical_support_expert, shipping_expert]

TOOL_CHAIN_MAP = {
    "billing_expert": billing_chain,
    "account_expert": account_chain,
    "technical_support_expert": technical_support_chain,
    "shipping_expert": shipping_chain,
}
