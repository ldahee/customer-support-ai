"""
FAQ CSV → ChromaDB 색인 스크립트.

사용 방법:
    cd backend

    # data/ 폴더 전체 일괄 색인 (서브폴더명이 카테고리)
    python -m mcp_servers.faq_search.indexer --data-dir ./data \
        --question-col FAQ_제목 --answer-col FAQ_내용 --reset

    # 단일 CSV 파일
    python -m mcp_servers.faq_search.indexer --csv ./data/한국안전교통공단/홈페이지FAQ.csv \
        --category 한국안전교통공단 --question-col FAQ_제목 --answer-col FAQ_내용

CSV 지원 형식:
    - 컬럼명은 --question-col / --answer-col 로 지정 (기본값: question / answer)
    - 인코딩은 utf-8 → cp949 순서로 자동 감지
    - 선택 컬럼: --category 미지정 시 폴더명 또는 파일명을 카테고리로 사용

옵션:
    --csv            단일 FAQ CSV 파일 경로
    --data-dir       data/ 최상위 폴더 경로 (서브폴더 전체 일괄 색인)
    --category       ChromaDB 메타데이터 카테고리값 (단일 파일 색인 시)
    --question-col   질문 컬럼명 (기본값: question)
    --answer-col     답변 컬럼명 (기본값: answer)
    --chroma         ChromaDB 저장 경로 (기본값: ./chroma_db)
    --collection     컬렉션 이름 (기본값: faq)
    --reset          기존 컬렉션 삭제 후 재색인
"""
import argparse
import csv
import logging
import os
import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 100


def detect_encoding(path: Path) -> str:
    """utf-8 → cp949 순서로 인코딩을 자동 감지합니다."""
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            with open(path, encoding=enc) as f:
                f.read(1024)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"


def read_csv(path: Path, question_col: str, answer_col: str) -> list[dict]:
    """CSV 파일을 읽어 {question, answer} 딕셔너리 목록으로 반환합니다."""
    encoding = detect_encoding(path)
    logger.info("'%s' 읽는 중 (인코딩: %s)", path.name, encoding)

    with open(path, newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        logger.warning("'%s' 파일이 비어 있습니다.", path.name)
        return []

    # 컬럼 존재 확인
    fieldnames = set(rows[0].keys())
    missing = {question_col, answer_col} - fieldnames
    if missing:
        logger.error(
            "'%s'에 필수 컬럼이 없습니다: %s\n사용 가능한 컬럼: %s",
            path.name,
            missing,
            fieldnames,
        )
        return []

    return [
        {
            "question": row[question_col].strip(),
            "answer": row[answer_col].strip(),
        }
        for row in rows
        if row.get(question_col, "").strip() and row.get(answer_col, "").strip()
    ]


def build_document(row: dict) -> str:
    return f"Q: {row['question']}\nA: {row['answer']}"


def index_csv(
    path: Path,
    category: str,
    question_col: str,
    answer_col: str,
    collection: "chromadb.Collection",
) -> int:
    """단일 CSV를 색인하고 색인된 행 수를 반환합니다."""
    rows = read_csv(path, question_col, answer_col)
    if not rows:
        return 0

    documents = [build_document(r) for r in rows]
    # category와 파일 경로를 조합해 고유 ID 생성
    id_prefix = f"{category}_{path.stem}"
    ids = [f"{id_prefix}_{i}" for i in range(len(rows))]
    metadatas = [
        {"category": category, "question": r["question"][:200]}
        for r in rows
    ]

    for start in range(0, len(documents), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(documents))
        collection.upsert(
            documents=documents[start:end],
            ids=ids[start:end],
            metadatas=metadatas[start:end],
        )
        logger.info("[%s] 색인 진행: %d / %d", category, end, len(documents))

    logger.info("[%s] '%s' → %d개 색인 완료", category, path.name, len(documents))
    return len(documents)


def run_indexer(
    csv_path: str | None,
    data_dir: str | None,
    category: str | None,
    question_col: str,
    answer_col: str,
    chroma_path: str,
    collection_name: str,
    reset: bool,
) -> None:
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    ef = OpenAIEmbeddingFunction(api_key=openai_api_key, model_name="text-embedding-3-small")
    client = chromadb.PersistentClient(path=chroma_path)

    if reset:
        try:
            client.delete_collection(collection_name)
            logger.info("기존 컬렉션 '%s' 삭제 완료", collection_name)
        except Exception:
            pass

    collection = client.get_or_create_collection(collection_name, embedding_function=ef)
    total_indexed = 0

    if data_dir:
        # --data-dir: 서브폴더 전체 스캔
        base = Path(data_dir)
        if not base.is_dir():
            logger.error("data-dir '%s'가 존재하지 않습니다.", data_dir)
            sys.exit(1)

        categories_found = [d for d in sorted(base.iterdir()) if d.is_dir()]
        if not categories_found:
            logger.error("'%s' 아래에 서브폴더가 없습니다.", data_dir)
            sys.exit(1)

        for cat_dir in categories_found:
            cat_name = cat_dir.name
            csv_files = list(cat_dir.glob("*.csv"))
            if not csv_files:
                logger.warning("[%s] CSV 파일이 없습니다. 건너뜀", cat_name)
                continue
            for csv_file in csv_files:
                total_indexed += index_csv(csv_file, cat_name, question_col, answer_col, collection)

    elif csv_path:
        # --csv: 단일 파일
        path = Path(csv_path)
        if not path.is_file():
            logger.error("CSV 파일 '%s'가 존재하지 않습니다.", csv_path)
            sys.exit(1)
        cat = category or path.parent.name
        total_indexed += index_csv(path, cat, question_col, answer_col, collection)

    else:
        logger.error("--csv 또는 --data-dir 중 하나를 반드시 지정해야 합니다.")
        sys.exit(1)

    logger.info("색인 완료: 총 %d개 FAQ → 컬렉션 '%s' (총 %d개)", total_indexed, collection_name, collection.count())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FAQ CSV → ChromaDB 색인")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv", help="단일 FAQ CSV 파일 경로")
    group.add_argument("--data-dir", help="data/ 최상위 폴더 (서브폴더 전체 일괄 색인)")
    parser.add_argument("--category", help="카테고리명 (--csv 사용 시, 미지정 시 폴더명 사용)")
    parser.add_argument("--question-col", default="question", help="질문 컬럼명 (기본값: question)")
    parser.add_argument("--answer-col", default="answer", help="답변 컬럼명 (기본값: answer)")
    parser.add_argument("--chroma", default="./chroma_db", help="ChromaDB 저장 경로")
    parser.add_argument("--collection", default="faq", help="컬렉션 이름")
    parser.add_argument("--reset", action="store_true", help="기존 컬렉션 삭제 후 재색인")
    args = parser.parse_args()

    run_indexer(
        csv_path=args.csv,
        data_dir=args.data_dir,
        category=args.category,
        question_col=args.question_col,
        answer_col=args.answer_col,
        chroma_path=args.chroma,
        collection_name=args.collection,
        reset=args.reset,
    )
