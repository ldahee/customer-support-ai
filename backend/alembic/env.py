import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from alembic import context

from app.config.settings import settings
from app.config.database import Base

# alembic.ini 로깅 설정
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 모델 메타데이터 (autogenerate 지원)
# 모든 모델을 import해야 Base.metadata에 등록됩니다
import app.repositories.inquiry_repository  # noqa: F401
target_metadata = Base.metadata


def get_url() -> str:
    url = settings.database_url
    if not url:
        raise RuntimeError("DATABASE_URL 환경변수가 설정되지 않았습니다.")
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    config_section = config.get_section(config.config_ini_section, {})
    config_section["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
