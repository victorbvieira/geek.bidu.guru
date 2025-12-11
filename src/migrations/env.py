"""
Alembic environment configuration for geek.bidu.guru.

Este arquivo configura o Alembic para usar SQLAlchemy async
e carregar todos os modelos automaticamente.
"""

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Adicionar src ao path para imports funcionarem
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.database import Base

# Importar todos os modelos para que o Alembic os detecte
from app.models import *  # noqa: F401, F403

# -----------------------------------------------------------------------------
# Alembic Config
# -----------------------------------------------------------------------------

config = context.config

# Configurar logging do Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData dos modelos para autogenerate
target_metadata = Base.metadata

# Sobrescrever sqlalchemy.url com variavel de ambiente
config.set_main_option("sqlalchemy.url", settings.database_url)


# -----------------------------------------------------------------------------
# Migrations Offline (gera SQL sem conectar ao banco)
# -----------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Gera SQL puro sem precisar de conexao com o banco.
    Util para review de migrations antes de aplicar.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# -----------------------------------------------------------------------------
# Migrations Online (conecta ao banco - modo async)
# -----------------------------------------------------------------------------


def do_run_migrations(connection: Connection) -> None:
    """Executa as migrations com uma conexao ativa."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Cria engine async e executa migrations.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Conecta ao banco de dados e executa as migrations.
    """
    asyncio.run(run_async_migrations())


# -----------------------------------------------------------------------------
# Executar
# -----------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
