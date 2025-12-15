"""Adiciona use_cases de IA para Occasion.

Revision ID: 012a
Revises: 0aa4c370add2
Create Date: 2025-12-14

Esta migration (parte 1 de 2):
- Adiciona novos valores ao ENUM ai_use_case para Occasion:
  - occasion_seo_all: Gera todos os campos SEO em JSON
  - occasion_seo_keyword: Gera palavra-chave foco
  - occasion_seo_title: Gera titulo SEO
  - occasion_seo_description: Gera meta description
  - occasion_content: Gera conteudo em Markdown

NOTA: Os INSERTs de dados estao na migration 012b para evitar
erro do PostgreSQL com valores ENUM novos na mesma transacao.

IMPORTANTE: ALTER TYPE ADD VALUE requer conexao separada com AUTOCOMMIT
pois asyncpg nao permite usar novos valores de ENUM na mesma sessao.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import create_engine, text

# revision identifiers, used by Alembic.
revision: str = "012a"
down_revision: Union[str, None] = "0aa4c370add2"
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
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_seo_all'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_seo_keyword'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_seo_title'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_seo_description'"))
        conn.execute(text("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_content'"))

    sync_engine.dispose()


def upgrade() -> None:
    """Adiciona novos valores ao ENUM ai_use_case para Occasion."""

    # Usar conexao separada com AUTOCOMMIT para ADD VALUE
    _add_enum_values_with_autocommit()


def downgrade() -> None:
    """Remove valores do ENUM.

    Nota: PostgreSQL nao permite remover valores de ENUM facilmente.
    Esta operacao seria destrutiva e pode quebrar dados existentes.
    """
    pass
