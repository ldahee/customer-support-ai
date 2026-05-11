import logging
from typing import Dict, List, Optional

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config.settings import settings

logger = logging.getLogger(__name__)


class MCPClientManager:
    """
    앱 수준 MCP 클라이언트 싱글턴.

    FastAPI lifespan에서 connect()/disconnect()를 한 번씩 호출한다.
    MCP URL이 하나도 설정되지 않았거나 연결에 실패하면 is_available == False가 되어
    각 expert chain은 MCP 없이 기존 동작으로 폴백한다.
    """

    def __init__(self) -> None:
        self._client: Optional[MultiServerMCPClient] = None
        self._tools_by_server: Dict[str, List[BaseTool]] = {}
        self._is_connected: bool = False

    @property
    def is_available(self) -> bool:
        return self._is_connected and self._client is not None

    def get_tools(self, server_name: str) -> List[BaseTool]:
        """설정된 MCP 서버의 tool 목록 반환. 미연결 시 빈 리스트."""
        if not self.is_available:
            return []
        return self._tools_by_server.get(server_name, [])

    async def connect(self) -> None:
        if not settings.mcp_enabled:
            logger.info("MCP disabled: no MCP server URLs configured")
            return

        try:
            self._client = MultiServerMCPClient(settings.mcp_server_configs)
            await self._client.__aenter__()

            for server_name in settings.mcp_server_configs:
                try:
                    server_tools = await self._client.get_tools(server_name=server_name)
                    self._tools_by_server[server_name] = server_tools
                    logger.info(
                        "MCP server '%s' connected: %d tools available %s",
                        server_name,
                        len(server_tools),
                        [t.name for t in server_tools],
                    )
                except Exception as e:
                    logger.warning("MCP server '%s' tool fetch failed: %s", server_name, e)
                    self._tools_by_server[server_name] = []

            self._is_connected = True
            logger.info("MCP client manager connected successfully")

        except Exception as e:
            logger.warning("MCP connection failed (continuing without MCP): %s", e)
            self._client = None
            self._is_connected = False

    async def disconnect(self) -> None:
        if self._client is not None:
            try:
                await self._client.__aexit__(None, None, None)
                logger.info("MCP client manager disconnected")
            except Exception as e:
                logger.warning("MCP disconnect error (ignored): %s", e)
            finally:
                self._client = None
                self._is_connected = False
                self._tools_by_server.clear()


mcp_manager = MCPClientManager()
