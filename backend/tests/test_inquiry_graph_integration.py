"""
통합 테스트: LangGraph end-to-end 흐름 (LLM 호출 모킹)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.router_output import RouterOutput
from app.schemas.expert_output import ExpertOutput, SafetyOutput


@pytest.fixture
def mock_router_output_billing():
    return RouterOutput(category="billing", confidence=0.93, routing_reason="결제 관련 문의")


@pytest.fixture
def mock_router_output_low_confidence():
    return RouterOutput(category="general", confidence=0.42, routing_reason="모호한 문의")


@pytest.fixture
def mock_expert_output():
    return ExpertOutput(answer="테스트 답변입니다.", answer_type="direct", escalation_needed=False)


@pytest.fixture
def mock_safety_output_safe():
    return SafetyOutput(is_safe=True, reason="일반 문의")


@pytest.fixture
def mock_safety_output_unsafe():
    return SafetyOutput(is_safe=False, reason="정책 위반")


@pytest.mark.asyncio
async def test_billing_routing_flow(
    mock_router_output_billing,
    mock_expert_output,
    mock_safety_output_safe,
):
    mock_billing_chain = MagicMock()
    mock_billing_chain.ainvoke = AsyncMock(return_value=mock_expert_output)

    with (
        patch("app.graphs.inquiry_graph.safety_chain") as mock_safety,
        patch("app.chains.router_chain.router_chain") as mock_router,
        patch(
            "app.chains.response_chain.CATEGORY_CHAIN_MAP",
            {"billing": mock_billing_chain},
        ),
    ):
        mock_safety.ainvoke = AsyncMock(return_value=mock_safety_output_safe)
        mock_router.ainvoke = AsyncMock(return_value=mock_router_output_billing)

        from app.graphs.inquiry_graph import inquiry_graph

        result = await inquiry_graph.ainvoke({
            "inquiry_text": "지난달 결제가 두 번 된 것 같아요.",
            "user_id": None,
            "channel": None,
            "locale": None,
            "inquiry_id": None,
            "category": None,
            "confidence": None,
            "routing_reason": None,
            "selected_agent": None,
            "answer": None,
            "safety_flag": None,
            "fallback_used": False,
            "retry_count": 0,
            "llm_call_count": 0,
            "error": None,
            "execution_trace": [],
        })

        assert result["category"] == "billing"
        assert result["selected_agent"] == "billing_expert_agent"
        assert result["fallback_used"] is False
        assert result["answer"] == "테스트 답변입니다."


@pytest.mark.asyncio
async def test_low_confidence_fallback_flow(
    mock_router_output_low_confidence,
    mock_expert_output,
    mock_safety_output_safe,
):
    with (
        patch("app.graphs.inquiry_graph.safety_chain") as mock_safety,
        patch("app.chains.router_chain.router_chain") as mock_router,
        patch("app.graphs.inquiry_graph.fallback_chain") as mock_fallback,
    ):
        mock_safety.ainvoke = AsyncMock(return_value=mock_safety_output_safe)
        mock_router.ainvoke = AsyncMock(return_value=mock_router_output_low_confidence)
        mock_fallback.ainvoke = AsyncMock(return_value=mock_expert_output)

        from app.graphs.inquiry_graph import inquiry_graph

        result = await inquiry_graph.ainvoke({
            "inquiry_text": "그냥 뭔가 이상해요.",
            "user_id": None,
            "channel": None,
            "locale": None,
            "inquiry_id": None,
            "category": None,
            "confidence": None,
            "routing_reason": None,
            "selected_agent": None,
            "answer": None,
            "safety_flag": None,
            "fallback_used": False,
            "retry_count": 0,
            "llm_call_count": 0,
            "error": None,
            "execution_trace": [],
        })

        assert result["fallback_used"] is True
        assert result["selected_agent"] == "general_fallback_agent"


@pytest.mark.asyncio
async def test_safety_blocked_flow(mock_safety_output_unsafe):
    with patch("app.graphs.inquiry_graph.safety_chain") as mock_safety:
        mock_safety.ainvoke = AsyncMock(return_value=mock_safety_output_unsafe)

        from app.graphs.inquiry_graph import inquiry_graph

        result = await inquiry_graph.ainvoke({
            "inquiry_text": "다른 사람 계정을 해킹하고 싶어요.",
            "user_id": None,
            "channel": None,
            "locale": None,
            "inquiry_id": None,
            "category": None,
            "confidence": None,
            "routing_reason": None,
            "selected_agent": None,
            "answer": None,
            "safety_flag": None,
            "fallback_used": False,
            "retry_count": 0,
            "llm_call_count": 0,
            "error": None,
            "execution_trace": [],
        })

        assert result["safety_flag"] is True
        assert result["selected_agent"] == "safety_agent"
        assert result["answer"] is not None
