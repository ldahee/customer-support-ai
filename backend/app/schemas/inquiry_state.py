from typing import Any, Optional
from typing_extensions import TypedDict


class ExecutionTraceItem(TypedDict, total=False):
    node_name: str
    status: str
    duration_ms: Optional[int]
    error: Optional[str]


class InquiryState(TypedDict):
    # Input
    inquiry_text: str
    user_id: Optional[str]
    channel: Optional[str]
    locale: Optional[str]
    inquiry_id: Optional[str]

    # Conversation
    conversation_id: Optional[str]
    chat_history: list[Any]  # list[BaseMessage]

    # Routing
    category: Optional[str]
    confidence: Optional[float]
    routing_reason: Optional[str]
    selected_agent: Optional[str]
    selected_agents: Optional[list[str]]  # v2: 복수 전문가 추적
    agent_version: Optional[str]          # "v1" | "v2"

    # Response
    answer: Optional[str]
    expert_answers: Optional[dict[str, str]]  # v2: synthesizer 입력용 중간 결과

    # v3: FAQ 검색 결과 (faq_retrieval_node에서 채워짐)
    faq_context: Optional[str]
    # v3: FAQ 카테고리 필터 (사용자가 선택한 카테고리, 빈 문자열이면 전체 검색)
    faq_category: Optional[str]

    # Safety
    safety_flag: Optional[bool]

    # Control
    fallback_used: bool
    retry_count: int
    llm_call_count: int
    error: Optional[str]

    # Execution trace
    execution_trace: list[ExecutionTraceItem]
