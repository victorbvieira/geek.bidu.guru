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
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012a"
down_revision: Union[str, None] = "0aa4c370add2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona novos valores ao ENUM ai_use_case para Occasion."""

    # Adicionar novos valores ao ENUM ai_use_case
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_seo_all'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_seo_keyword'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_seo_title'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_seo_description'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_content'")


def downgrade() -> None:
    """Remove valores do ENUM.

    Nota: PostgreSQL nao permite remover valores de ENUM facilmente.
    Esta operacao seria destrutiva e pode quebrar dados existentes.
    """
    pass
