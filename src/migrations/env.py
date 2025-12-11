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
from sqlalchemy.ext.asyncio import create_async_engine

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

# URL do banco de dados (direto do settings, sem passar pelo ConfigParser)
DATABASE_URL = settings.database_url


# -----------------------------------------------------------------------------
# Migrations Offline (gera SQL sem conectar ao banco)
# -----------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Gera SQL puro sem precisar de conexao com o banco.
    Util para review de migrations antes de aplicar.
    """
    context.configure(
        url=DATABASE_URL,
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
    # Criar engine diretamente com a URL (evita problemas com caracteres especiais)
    connectable = create_async_engine(
        DATABASE_URL,
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
