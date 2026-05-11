import json
from typing import Any, Dict, List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_base_url: Optional[str] = None

    # Model per agent
    router_model: str = "gpt-4o-mini"
    billing_model: str = "gpt-4o-mini"
    account_model: str = "gpt-4o-mini"
    technical_support_model: str = "gpt-4o-mini"
    shipping_model: str = "gpt-4o-mini"
    fallback_model: str = "gpt-4o-mini"
    safety_model: str = "gpt-4o-mini"
    orchestrator_model: str = "gpt-4o-mini"
    synthesizer_model: str = "gpt-4o-mini"

    # Routing policy
    routing_confidence_low_threshold: float = 0.50
    max_llm_calls: int = 5
    max_retry_count: int = 2

    # Database
    database_url: Optional[str] = None

    # MCP 서버 설정 (v3 전용, 선택적 — 미설정 시 MCP 비활성화)
    mcp_faq_url: Optional[str] = None         # FAQSearch MCP 서버 URL
    mcp_slack_url: Optional[str] = None       # SlackNotify MCP 서버 URL
    mcp_connect_timeout: float = 5.0
    mcp_tool_timeout: float = 10.0

    # FAQ MCP 서버 자체 설정 (mcp_servers/faq_search/server.py 에서 읽음)
    faq_chroma_path: str = "./chroma_db"
    faq_collection_name: str = "faq"

    # Slack MCP 서버 자체 설정 (mcp_servers/slack_notify/server.py 에서 읽음)
    slack_webhook_url: Optional[str] = None

    @property
    def mcp_enabled(self) -> bool:
        return any([self.mcp_faq_url, self.mcp_slack_url])

    @property
    def mcp_server_configs(self) -> Dict[str, Dict[str, Any]]:
        configs: Dict[str, Dict[str, Any]] = {}
        if self.mcp_faq_url:
            configs["faq"] = {"url": self.mcp_faq_url, "transport": "streamable_http"}
        if self.mcp_slack_url:
            configs["slack"] = {"url": self.mcp_slack_url, "transport": "streamable_http"}
        return configs

    # Environment
    environment: str = "development"  # "development" | "production"

    # Security
    # ALLOWED_ORIGINS: JSON 배열 또는 쉼표 구분 문자열 e.g. '["https://app.example.com"]' 또는 'https://app.example.com'
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    # API 키가 설정된 경우 모든 요청에 X-API-Key 헤더 필요
    api_key: Optional[str] = None
    # 운영자 모드(mode=operator) 접근에 필요한 별도 키
    operator_api_key: Optional[str] = None
    # Rate limiting: slowapi 형식 e.g. "20/minute"
    rate_limit: str = "20/minute"
    # 사용자당 일별 요청 제한 (KST 자정 기준 초기화)
    daily_limit: int = 10

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            return ["http://localhost:3000"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
