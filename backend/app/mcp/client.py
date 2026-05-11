import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config.settings import settings

logger = logging.getLogger(__name__)


class MCPClientManager:
    """
    앱 수준 MCP 클라이언트 싱글턴.

    langchain-mcp-adapters 0.2.x에서 get_tools(server_name=...)를 사용한다.
    각 툴 호출 시 자체 커넥션을 생성하므로 세션 관리가 불필요하다.
    MCP URL이 설정되지 않았거나 연결에 실패하면 빈 tool 목록을 반환해
    v3 노드가 graceful degradation한다.
    """

    def __init__(self) -> None:
        self._is_enabled: bool = False

    @property
    def is_available(self) -> bool:
        return self._is_enabled

    async def connect(self) -> None:
        if settings.mcp_enabled:
            self._is_enabled = True
            logger.info("MCP enabled: %s", list(settings.mcp_server_configs.keys()))
            for name, cfg in settings.mcp_server_configs.items():
                logger.info("  - %s: %s", name, cfg.get("url", "(없음)"))
        else:
            logger.info("MCP disabled (mcp_faq_url=%r, mcp_slack_url=%r)",
                        settings.mcp_faq_url, settings.mcp_slack_url)

    async def disconnect(self) -> None:
        self._is_enabled = False

    @asynccontextmanager
    async def session_tools(self, server_name: str) -> AsyncIterator[List[BaseTool]]:
        """서버별 tools를 로드해 yield하는 context manager."""
        if not self.is_available or server_name not in settings.mcp_server_configs:
            yield []
            return

        try:
            client = MultiServerMCPClient({server_name: settings.mcp_server_configs[server_name]})
            tools = await client.get_tools(server_name=server_name)
            logger.info("MCP '%s': %d tools loaded", server_name, len(tools))
            yield tools
        except Exception as e:
            logger.warning("MCP '%s' failed (continuing without): %s", server_name, e)
            yield []


mcp_manager = MCPClientManager()
