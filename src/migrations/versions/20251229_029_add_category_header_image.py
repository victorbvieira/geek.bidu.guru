"""Adiciona campo header_image_url a tabela categories.

Revision ID: 029
Revises: 028
Create Date: 2025-12-29

Campos adicionados:
- header_image_url: URL da imagem de fundo do header da categoria (1920x400 px recomendado)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "029"
down_revision: Union[str, None] = "028"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona campo header_image_url a tabela categories."""
    op.add_column(
        "categories",
        sa.Column(
            "header_image_url",
            sa.String(500),
            nullable=True,
            comment="Imagem de fundo do header da categoria (1920x400 px recomendado)",
        ),
    )


def downgrade() -> None:
    """Remove campo header_image_url da tabela categories."""
    op.drop_column("categories", "header_image_url")
