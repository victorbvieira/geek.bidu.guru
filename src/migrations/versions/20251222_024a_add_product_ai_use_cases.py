"""Adiciona use_cases de IA para Product (tags e Instagram).

Revision ID: 024a
Revises: 023
Create Date: 2025-12-22

Esta migration (parte 1 de 3):
- Adiciona novos valores ao ENUM ai_use_case para Product:
  - product_tags: Gera tags do produto
  - product_instagram_headline: Gera headline para Instagram
  - product_instagram_badge: Gera badge para Instagram
  - product_instagram_title: Gera titulo para Instagram
  - product_instagram_hashtags: Gera hashtags para Instagram
  - product_instagram_caption: Gera caption para Instagram
  - product_instagram_all: Gera todos os campos Instagram

NOTA: Os INSERTs de dados estao na migration 024c.

IMPORTANTE: ALTER TYPE ADD VALUE requer conexao separada com AUTOCOMMIT
pois asyncpg nao permite usar novos valores de ENUM na mesma sessao.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import create_engine, text

# revision identifiers, used by Alembic.
revision: str = "024a"
down_revision: Union[str, None] = "023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_enum_values_with_autocommit() -> None:
    """
    Adiciona novos valores ao ENUM usando conexao sincrona com AUTOCOMMIT.

    PostgreSQL requer que ALTER TYPE ADD VALUE seja executado fora de uma
    transaction block. Usamos psycopg2 com AUTOCOMMIT para isso.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.config import settings

    # Converte URL async para sync (psycopg2)
    sync_url = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )

    sync_engine = create_engine(sync_url, isolation_level="AUTOCOMMIT")

    with sync_engine.connect() as conn:
        # Adiciona valores do enum para Product - Tags
        conn.execute(text(
            "ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'product_tags'"
        ))

        # Adiciona valores do enum para Product - Instagram
        conn.execute(text(
            "ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'product_instagram_headline'"
        ))
        conn.execute(text(
            "ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'product_instagram_badge'"
        ))
        conn.execute(text(
            "ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'product_instagram_title'"
        ))
        conn.execute(text(
            "ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'product_instagram_hashtags'"
        ))
        conn.execute(text(
            "ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'product_instagram_caption'"
        ))
        conn.execute(text(
            "ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'product_instagram_all'"
        ))

    sync_engine.dispose()


def upgrade() -> None:
    """Adiciona novos valores ao ENUM ai_use_case para Product."""

    # Usar conexao separada com AUTOCOMMIT para ADD VALUE
    _add_enum_values_with_autocommit()


def downgrade() -> None:
    """PostgreSQL nao permite remover valores de ENUM facilmente.

    Para reverter, seria necessario:
    1. Criar novo tipo ENUM sem os valores
    2. Atualizar todas as colunas que usam o tipo
    3. Remover o tipo antigo
    4. Renomear o novo tipo

    Isso e complexo e arriscado, entao deixamos vazio.
    """
    pass
