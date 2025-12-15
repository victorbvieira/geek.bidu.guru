"""Adiciona ENUM ai_entity e coluna entity em ai_configs.

Revision ID: 008a
Revises: 007
Create Date: 2025-12-14

Esta migration (parte 1 de 2):
- Adiciona ENUM ai_entity (post, category, occasion, product, general)
- Adiciona novos valores ao ENUM ai_use_case
- Adiciona coluna entity em ai_configs

NOTA: Os INSERTs de dados estao na migration 008b para evitar
erro do PostgreSQL com valores ENUM novos na mesma transacao.

IMPORTANTE: ALTER TYPE ADD VALUE requer conexao separada com AUTOCOMMIT
pois asyncpg nao permite usar novos valores de ENUM na mesma sessao.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import create_engine, text

# revision identifiers, used by Alembic.
revision: str = "008a"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_enum_values_with_autocommit() -> None:
    """
    Adiciona novos valores ao ENUM usando conexao sincrona com AUTOCOMMIT.

    asyncpg nao permite usar novos valores de ENUM na mesma sessao em que
    foram criados, mesmo apos COMMIT. A solucao e usar uma conexao separada
    com psycopg2 (sincrono) em modo AUTOCOMMIT.
    """
    # Importar settings para pegar a URL do banco
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.config import settings

    # Converter URL async para sync (asyncpg -> psycopg2)
    sync_url = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )

    # Criar engine sincrona com isolation_level AUTOCOMMIT
    sync_engine = create_engine(
        sync_url,
        isolation_level="AUTOCOMMIT"
    )

    # Adicionar valores ao ENUM (cada um e auto-commitado imediatamente)
    with sync_engine.connect() as conn:
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_seo_all'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_seo_keyword'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_seo_title'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_seo_description'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_tags'"))

    sync_engine.dispose()


def upgrade() -> None:
    """Adiciona ENUMs e coluna entity."""

    # 1. Criar ENUM ai_entity
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE ai_entity AS ENUM ('post', 'category', 'occasion', 'product', 'general');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$
    """)

    # 2. Adicionar novos valores ao ENUM ai_use_case usando conexao separada
    # IMPORTANTE: asyncpg requer que ADD VALUE seja commitado em sessao separada
    _add_enum_values_with_autocommit()

    # 3. Adicionar coluna entity na tabela ai_configs
    op.execute("""
        ALTER TABLE ai_configs
        ADD COLUMN IF NOT EXISTS entity ai_entity DEFAULT 'general'
    """)

    # 4. Atualizar registros existentes com entity 'general'
    op.execute("""
        UPDATE ai_configs
        SET entity = 'general'
        WHERE entity IS NULL
    """)

    # 5. Criar indice para entity
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_ai_configs_entity ON ai_configs(entity)
    """)


def downgrade() -> None:
    """Remove coluna entity e indice."""

    # Remove indice
    op.execute("DROP INDEX IF EXISTS idx_ai_configs_entity")

    # Remove coluna entity
    op.execute("ALTER TABLE ai_configs DROP COLUMN IF EXISTS entity")

    # Nota: NAO removemos os ENUMs pois pode quebrar outras coisas
    # e o PostgreSQL nao permite remover valores de ENUM facilmente
