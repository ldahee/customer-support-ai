"""
SlackNotify MCP 서버.

Slack Incoming Webhook으로 알림을 발송합니다.

실행 방법:
    cd backend
    python -m mcp_servers.slack_notify.server

환경변수:
    SLACK_WEBHOOK_URL  Slack Incoming Webhook URL (필수)
    MCP_SLACK_HOST     서버 바인딩 호스트 (기본값: 0.0.0.0)
    MCP_SLACK_PORT     서버 포트 (기본값: 8011)
"""
import logging
import os

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
HOST = os.environ.get("MCP_SLACK_HOST", "0.0.0.0")
# Railway는 PORT를 자동 주입함. 로컬에서는 MCP_SLACK_PORT(기본 8011) 사용
PORT = int(os.environ.get("PORT", os.environ.get("MCP_SLACK_PORT", "8011")))

if not SLACK_WEBHOOK_URL:
    logger.warning("SLACK_WEBHOOK_URL이 설정되지 않았습니다. 알림이 발송되지 않습니다.")

mcp = FastMCP("slack-notify")


@mcp.tool()
async def slack_notify(message: str) -> str:
    """
    Slack 채널로 알림 메시지를 발송합니다.

    Args:
        message: 발송할 메시지 (마크다운 지원)

    Returns:
        "sent" (성공) 또는 에러 메시지
    """
    if not SLACK_WEBHOOK_URL:
        return "skipped: SLACK_WEBHOOK_URL not set"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                SLACK_WEBHOOK_URL,
                json={"text": message},
            )
            response.raise_for_status()
        logger.info("Slack 알림 발송 완료")
        return "sent"
    except httpx.HTTPStatusError as e:
        logger.error("Slack 알림 실패 (HTTP %d): %s", e.response.status_code, e)
        return f"error: HTTP {e.response.status_code}"
    except Exception as e:
        logger.error("Slack 알림 실패: %s", e)
        return f"error: {e}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=HOST, port=PORT, path="/mcp")
