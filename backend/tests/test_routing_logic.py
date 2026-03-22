"""
단위 테스트: 라우팅 threshold 로직 및 에이전트 선택
"""
import pytest

from app.graphs.inquiry_graph import route_after_safety, route_after_router
from app.schemas.inquiry_state import InquiryState


def _make_state(**kwargs) -> InquiryState:
    defaults: InquiryState = {
        "inquiry_text": "테스트 문의",
        "user_id": None,
        "channel": None,
        "locale": None,
        "inquiry_id": "test-id",
        "category": "general",
        "confidence": 0.9,
        "routing_reason": None,
        "selected_agent": None,
        "answer": None,
        "safety_flag": False,
        "fallback_used": False,
        "retry_count": 0,
        "llm_call_count": 0,
        "error": None,
        "execution_trace": [],
    }
    defaults.update(kwargs)
    return defaults


class TestRoutingAfterSafety:
    def test_safe_request_goes_to_router(self):
        state = _make_state(safety_flag=False)
        assert route_after_safety(state) == "router_node"

    def test_unsafe_request_goes_to_safe_response(self):
        state = _make_state(safety_flag=True)
        assert route_after_safety(state) == "safe_response_node"


class TestRoutingAfterRouter:
    def test_billing_high_confidence(self):
        state = _make_state(category="billing", confidence=0.93)
        assert route_after_router(state) == "billing_agent_node"

    def test_account_high_confidence(self):
        state = _make_state(category="account", confidence=0.85)
        assert route_after_router(state) == "account_agent_node"

    def test_technical_support_high_confidence(self):
        state = _make_state(category="technical_support", confidence=0.88)
        assert route_after_router(state) == "technical_support_agent_node"

    def test_shipping_high_confidence(self):
        state = _make_state(category="shipping", confidence=0.91)
        assert route_after_router(state) == "shipping_agent_node"

    def test_low_confidence_goes_to_fallback(self):
        # confidence < 0.50 → fallback
        state = _make_state(category="billing", confidence=0.42)
        assert route_after_router(state) == "fallback_agent_node"

    def test_general_category_goes_to_fallback(self):
        state = _make_state(category="general", confidence=0.6)
        assert route_after_router(state) == "fallback_agent_node"

    def test_zero_confidence_goes_to_fallback(self):
        state = _make_state(category="billing", confidence=0.0)
        assert route_after_router(state) == "fallback_agent_node"
