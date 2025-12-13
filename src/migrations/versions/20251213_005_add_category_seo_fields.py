"""Adiciona campos SEO e imagem a tabela categories.

Revision ID: 005
Revises: 004
Create Date: 2025-12-13

Campos adicionados:
- image_url: URL da imagem de capa da categoria
- seo_title: Titulo para SEO (max 60 caracteres)
- seo_description: Meta description (max 160 caracteres)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona campos SEO e imagem a tabela categories."""
    # Adiciona coluna image_url
    op.add_column(
        "categories",
        sa.Column("image_url", sa.String(500), nullable=True),
    )

    # Adiciona coluna seo_title
    op.add_column(
        "categories",
        sa.Column("seo_title", sa.String(60), nullable=True),
    )

    # Adiciona coluna seo_description
    op.add_column(
        "categories",
        sa.Column("seo_description", sa.String(160), nullable=True),
    )


def downgrade() -> None:
    """Remove campos SEO e imagem da tabela categories."""
    op.drop_column("categories", "seo_description")
    op.drop_column("categories", "seo_title")
    op.drop_column("categories", "image_url")
