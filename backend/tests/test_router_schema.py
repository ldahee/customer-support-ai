"""
단위 테스트: Router 스키마 파싱 및 threshold 로직
"""
import pytest
from pydantic import ValidationError

from app.schemas.router_output import RouterOutput


def test_router_output_valid():
    result = RouterOutput(category="billing", confidence=0.95, routing_reason="결제 문의")
    assert result.category == "billing"
    assert result.confidence == 0.95


def test_router_output_invalid_category():
    with pytest.raises(ValidationError):
        RouterOutput(category="invalid_category", confidence=0.9, routing_reason="test")


def test_router_output_confidence_out_of_range():
    with pytest.raises(ValidationError):
        RouterOutput(category="billing", confidence=1.5, routing_reason="test")

    with pytest.raises(ValidationError):
        RouterOutput(category="billing", confidence=-0.1, routing_reason="test")


def test_router_output_all_categories():
    for cat in ["billing", "account", "technical_support", "shipping", "general"]:
        result = RouterOutput(category=cat, confidence=0.8, routing_reason="test")
        assert result.category == cat
