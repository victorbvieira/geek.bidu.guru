"""Adiciona use_cases de IA para Category.

Revision ID: 019a
Revises: 018
Create Date: 2025-12-14

Esta migration (parte 1 de 2):
- Adiciona novos valores ao ENUM ai_use_case para Category:
  - category_seo_keyword: Gera palavra-chave foco
  - category_seo_title: Gera titulo SEO
  - category_seo_description: Gera meta description
  - category_tags: Gera tags

NOTA: Os INSERTs de dados estao na migration 019b.

IMPORTANTE: ALTER TYPE ADD VALUE requer conexao separada com AUTOCOMMIT
pois asyncpg nao permite usar novos valores de ENUM na mesma sessao.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import create_engine, text

# revision identifiers, used by Alembic.
revision: str = "019a"
down_revision: Union[str, None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_enum_values_with_autocommit() -> None:
    """
    Adiciona novos valores ao ENUM usando conexao sincrona com AUTOCOMMIT.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.config import settings

    sync_url = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )

    sync_engine = create_engine(sync_url, isolation_level="AUTOCOMMIT")

    with sync_engine.connect() as conn:
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'category_seo_keyword'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'category_seo_title'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'category_seo_description'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'category_tags'"))

    sync_engine.dispose()


def upgrade() -> None:
    """Adiciona novos valores ao ENUM ai_use_case para Category."""

    # Usar conexao separada com AUTOCOMMIT para ADD VALUE
    _add_enum_values_with_autocommit()


def downgrade() -> None:
    """PostgreSQL nao permite remover valores de ENUM facilmente."""
    pass
