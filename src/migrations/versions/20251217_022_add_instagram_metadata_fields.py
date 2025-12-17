"""
Adiciona campos de metadados para posts Instagram na tabela products.

Campos adicionados:
- instagram_headline: Headline de impacto (ex: OFERTA IMPERDIVEL!)
- instagram_title: Titulo curto para Instagram
- instagram_badge: Texto do badge (ex: NOVO!, BEST SELLER)
- instagram_caption: Caption pre-definida para posts
- instagram_hashtags: Lista de hashtags (JSONB)

Estes campos permitem pre-configurar o conteudo de posts no cadastro
do produto, facilitando a republicacao futura.

Revision ID: 022
Revises: 021
Create Date: 2025-12-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# Identificadores da migration
revision: str = "022"
down_revision: str = "021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Adiciona campos de metadados Instagram na tabela products.
    """
    # Headline de impacto
    op.add_column(
        "products",
        sa.Column(
            "instagram_headline",
            sa.String(50),
            nullable=True,
            comment="Headline de impacto para Instagram (ex: OFERTA IMPERDIVEL!)"
        )
    )

    # Titulo curto
    op.add_column(
        "products",
        sa.Column(
            "instagram_title",
            sa.String(100),
            nullable=True,
            comment="Titulo curto para Instagram (se diferente do nome)"
        )
    )

    # Texto do badge
    op.add_column(
        "products",
        sa.Column(
            "instagram_badge",
            sa.String(30),
            nullable=True,
            comment="Texto do badge (ex: NOVO!, BEST SELLER)"
        )
    )

    # Caption pre-definida
    op.add_column(
        "products",
        sa.Column(
            "instagram_caption",
            sa.Text(),
            nullable=True,
            comment="Caption pre-definida para posts Instagram"
        )
    )

    # Lista de hashtags
    op.add_column(
        "products",
        sa.Column(
            "instagram_hashtags",
            JSONB(),
            nullable=False,
            server_default="[]",
            comment="Lista de hashtags para Instagram"
        )
    )


def downgrade() -> None:
    """
    Remove os campos de metadados Instagram.
    """
    op.drop_column("products", "instagram_hashtags")
    op.drop_column("products", "instagram_caption")
    op.drop_column("products", "instagram_badge")
    op.drop_column("products", "instagram_title")
    op.drop_column("products", "instagram_headline")
