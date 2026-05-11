import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.faq_router import router as faq_router
from app.api.inquiry_router import router as inquiry_router
from app.config.settings import settings
from app.mcp.client import mcp_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# pydantic-settings 처리 전 raw 환경변수 값 출력 (진단용)
_logger = logging.getLogger(__name__)
_logger.info(
    "RAW ENV: MCP_FAQ_URL=%r  MCP_SLACK_URL=%r",
    os.environ.get("MCP_FAQ_URL"),
    os.environ.get("MCP_SLACK_URL"),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mcp_manager.connect()
    yield
    await mcp_manager.disconnect()


app = FastAPI(
    title="고객 문의 자동응답 시스템",
    description="LangChain + LangGraph 기반 멀티 에이전트 문의 분류 및 답변 생성 시스템",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inquiry_router)
app.include_router(faq_router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
