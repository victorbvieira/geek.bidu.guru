"""Adiciona campo seo_focus_keyword em categorias e ocasioes.

Revision ID: 007
Revises: 006
Create Date: 2025-12-14

Padroniza campos SEO em todas as entidades:
- categories: adiciona seo_focus_keyword
- occasions: adiciona seo_focus_keyword
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona seo_focus_keyword em categories e occasions."""

    # Adiciona coluna em categories
    op.add_column(
        "categories",
        sa.Column("seo_focus_keyword", sa.String(100), nullable=True)
    )

    # Adiciona coluna em occasions
    op.add_column(
        "occasions",
        sa.Column("seo_focus_keyword", sa.String(100), nullable=True)
    )


def downgrade() -> None:
    """Remove seo_focus_keyword de categories e occasions."""

    op.drop_column("occasions", "seo_focus_keyword")
    op.drop_column("categories", "seo_focus_keyword")
