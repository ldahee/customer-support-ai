"""
FAQ 관련 유틸리티 API.
"""
import csv
import random
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/faq", tags=["faq"])

# FastAPI 앱은 backend/ 디렉토리에서 실행되므로 data/ 경로는 backend/data/ 를 가리킴
_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_SAMPLE_SIZE = 5


def _detect_encoding(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            with open(path, encoding=enc) as f:
                f.read(1024)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"


def _read_questions(path: Path) -> list[str]:
    encoding = _detect_encoding(path)
    with open(path, newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return []
    fieldnames = list(rows[0].keys())
    question_col = next(
        (c for c in ("FAQ_제목", "question") if c in fieldnames),
        fieldnames[0],
    )
    return [row[question_col].strip() for row in rows if row.get(question_col, "").strip()]


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


@router.get("/questions", summary="FAQ 카테고리의 예시 질문 샘플 반환")
async def list_faq_questions(category: str = "") -> list[str]:
    """
    특정 카테고리 CSV에서 질문을 최대 5개 무작위로 반환합니다.

    Returns:
        질문 문자열 목록 (최대 5개), category가 없거나 찾을 수 없으면 빈 리스트
    """
    if not category:
        return []
    cat_dir = _DATA_DIR / category
    if not cat_dir.is_dir():
        return []
    questions: list[str] = []
    for csv_file in cat_dir.glob("*.csv"):
        questions.extend(_read_questions(csv_file))
    if not questions:
        return []
    return random.sample(questions, min(_SAMPLE_SIZE, len(questions)))
