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
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008a"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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

    # 2. Adicionar novos valores ao ENUM ai_use_case
    # PostgreSQL nao permite adicionar valores em transacao com uso imediato,
    # mas aqui apenas adicionamos os valores sem usar
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_seo_all'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_seo_keyword'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_seo_title'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_seo_description'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'post_tags'")

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
