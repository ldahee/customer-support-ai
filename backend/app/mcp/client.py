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

    langchain-mcp-adapters 0.1.0+에서 MultiServerMCPClient는 context manager로
    사용할 수 없다. 대신 session_tools()로 호출 시점에 세션을 열고 닫는다.
    MCP URL이 설정되지 않았거나 세션 연결에 실패하면 빈 tool 목록을 반환해
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
        else:
            logger.info("MCP disabled: no MCP server URLs configured")

    async def disconnect(self) -> None:
        self._is_enabled = False

    @asynccontextmanager
    async def session_tools(self, server_name: str) -> AsyncIterator[List[BaseTool]]:
        """서버별 세션을 열어 tools를 yield하고 닫는 context manager."""
        if not self.is_available or server_name not in settings.mcp_server_configs:
            yield []
            return

        try:
            client = MultiServerMCPClient({server_name: settings.mcp_server_configs[server_name]})
            async with client.session(server_name) as session:
                from langchain_mcp_adapters.tools import load_mcp_tools
                tools = await load_mcp_tools(session)
                logger.info("MCP '%s': %d tools loaded", server_name, len(tools))
                yield tools
        except Exception as e:
            logger.warning("MCP '%s' session failed (continuing without): %s", server_name, e)
            yield []


mcp_manager = MCPClientManager()
