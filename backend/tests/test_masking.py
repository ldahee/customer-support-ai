"""
단위 테스트: 개인정보 마스킹
"""
from app.repositories.inquiry_repository import mask_pii


def test_email_masking():
    text = "이메일은 user@example.com 입니다."
    assert "[EMAIL]" in mask_pii(text)
    assert "user@example.com" not in mask_pii(text)


def test_phone_masking():
    text = "전화번호는 010-1234-5678 입니다."
    masked = mask_pii(text)
    assert "[PHONE]" in masked
    assert "010-1234-5678" not in masked


def test_card_number_masking():
    text = "카드번호는 1234-5678-9012-3456 입니다."
    masked = mask_pii(text)
    assert "[CARD]" in masked
    assert "1234-5678-9012-3456" not in masked


def test_rrn_masking():
    text = "주민번호는 900101-1234567 입니다."
    masked = mask_pii(text)
    assert "[RRN]" in masked
    assert "900101-1234567" not in masked


def test_no_personal_info():
    text = "배송 조회를 하고 싶어요."
    assert mask_pii(text) == text


def test_multiple_pii():
    text = "이메일 user@test.com, 전화 01012345678"
    masked = mask_pii(text)
    assert "[EMAIL]" in masked
    assert "[PHONE]" in masked
