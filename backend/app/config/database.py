"""
SQLAlchemy async 엔진 및 세션 팩토리.
DATABASE_URL이 설정되지 않은 경우 DB 기능은 비활성화됩니다.
"""
import ssl
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

if settings.database_url:
    if settings.environment == "production":
        _ssl_arg = True  # Vercel(Linux): 시스템 CA 인증서로 정상 검증
    else:
        _ssl_context = ssl.create_default_context()
        _ssl_context.check_hostname = False
        _ssl_context.verify_mode = ssl.CERT_NONE
        _ssl_arg = _ssl_context  # 로컬 macOS: 인증서 검증 스킵

    _engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        connect_args={"ssl": _ssl_arg},
    )
    _session_factory = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        raise RuntimeError("DATABASE_URL이 설정되지 않아 DB 세션을 생성할 수 없습니다.")
    async with _session_factory() as session:
        yield session


def is_db_enabled() -> bool:
    return _session_factory is not None
