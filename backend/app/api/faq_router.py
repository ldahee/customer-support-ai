"""
FAQ 관련 유틸리티 API.
"""
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/faq", tags=["faq"])

# FastAPI 앱은 backend/ 디렉토리에서 실행되므로 data/ 경로는 backend/data/ 를 가리킴
_DATA_DIR = Path(__file__).parent.parent.parent / "data"


@router.get("/categories", summary="색인된 FAQ 카테고리 목록 반환")
async def list_faq_categories() -> list[str]:
    """
    data/ 폴더의 서브폴더명을 FAQ 카테고리로 반환합니다.

    Returns:
        카테고리 이름 목록 (예: ["한국안전교통공단"])
        data/ 폴더가 없거나 서브폴더가 없으면 빈 리스트 반환
    """
    if not _DATA_DIR.is_dir():
        return []
    return sorted(d.name for d in _DATA_DIR.iterdir() if d.is_dir())
