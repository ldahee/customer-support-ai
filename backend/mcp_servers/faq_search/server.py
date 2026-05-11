"""
FAQSearch MCP 서버.

chromadb에 색인된 FAQ 데이터를 시맨틱 검색으로 조회합니다.
category 파라미터로 특정 카테고리의 FAQ만 검색할 수 있습니다.

실행 방법:
    cd backend
    python -m mcp_servers.faq_search.server

환경변수:
    OPENAI_API_KEY       OpenAI API 키 (임베딩 생성용)
    FAQ_CHROMA_PATH      ChromaDB 저장 경로 (기본값: ./chroma_db)
    FAQ_COLLECTION_NAME  ChromaDB 컬렉션 이름 (기본값: faq)
    MCP_FAQ_HOST         서버 바인딩 호스트 (기본값: 0.0.0.0)
    MCP_FAQ_PORT         서버 포트 (기본값: 8010)
"""
import logging
import os
from contextlib import asynccontextmanager

import chromadb
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CHROMA_PATH = os.environ.get("FAQ_CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.environ.get("FAQ_COLLECTION_NAME", "faq")
HOST = os.environ.get("MCP_FAQ_HOST", "0.0.0.0")
# Railway는 PORT를 자동 주입함. 로컬에서는 MCP_FAQ_PORT(기본 8010) 사용
PORT = int(os.environ.get("PORT", os.environ.get("MCP_FAQ_PORT", "8010")))

try:
    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

    _ef = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name="text-embedding-3-small")
    _client = chromadb.PersistentClient(path=CHROMA_PATH)
    _collection = _client.get_or_create_collection(COLLECTION_NAME, embedding_function=_ef)
    logger.info("ChromaDB collection '%s' loaded (%d docs)", COLLECTION_NAME, _collection.count())
except Exception as e:
    logger.error("ChromaDB 초기화 실패: %s", e)
    _collection = None

mcp = FastMCP("faq-search", host=HOST, port=PORT)


async def _health(request):
    return JSONResponse({"status": "ok"})


_mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app):
    async with _mcp_app.router.lifespan_context(_mcp_app):
        yield


asgi_app = Starlette(
    lifespan=lifespan,
    routes=[
        Route("/health", _health),
        Mount("/", app=_mcp_app),
    ],
)


@mcp.tool()
async def faq_search(query: str, category: str = "", top_k: int = 3) -> str:
    """
    FAQ에서 질문과 관련된 내용을 검색합니다.

    Args:
        query:    검색할 문의 내용 (자연어)
        category: 검색할 카테고리 (빈 문자열이면 전체 검색)
        top_k:    반환할 최대 결과 수 (기본값: 3)

    Returns:
        관련 FAQ 항목들 (Q&A 형식), 없으면 빈 문자열
    """
    if _collection is None:
        return ""

    count = _collection.count()
    if count == 0:
        logger.warning("FAQ 컬렉션이 비어 있습니다. indexer.py를 먼저 실행하세요.")
        return ""

    where = {"category": category} if category else None

    try:
        results = _collection.query(
            query_texts=[query],
            n_results=min(top_k, count),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        logger.error("ChromaDB 쿼리 실패: %s", e)
        return ""

    docs = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not docs:
        return ""

    parts = [
        doc
        for doc, dist in zip(docs, distances)
        if dist <= 0.8  # 코사인 거리 0.8 초과는 관련성 낮음으로 제외
    ]

    return "\n\n---\n\n".join(parts) if parts else ""


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
