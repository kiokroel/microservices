import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from src.core.config import settings  # noqa: E402
from src.core.database import WorkerBase  # noqa: E402
from src.models import *  # noqa: F401,F403,E402

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = WorkerBase.metadata

config.set_main_option(
    "sqlalchemy.url",
    settings.worker_db_settings.database_url,
)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
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


async def run_migrations_online():
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

