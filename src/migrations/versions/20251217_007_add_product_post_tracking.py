"""
Adiciona campos de controle de posts em redes sociais na tabela products.

Campos adicionados:
- last_post_date: Data do ultimo post sobre o produto
- post_count: Contador de quantas vezes o produto foi postado
- last_post_platform: Plataforma do ultimo post (instagram, tiktok, etc)
- last_post_url: URL do ultimo post publicado

Revision ID: 007_add_product_post_tracking
Revises: 20251213_f626ead1bfd0
Create Date: 2025-12-17
"""

from alembic import op
import sqlalchemy as sa


# Identificadores da migration
revision: str = "021"
down_revision: str = "020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Adiciona campos de controle de posts na tabela products.
    """
    # Adicionar colunas
    op.add_column(
        "products",
        sa.Column(
            "last_post_date",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Data do ultimo post sobre este produto"
        )
    )

    op.add_column(
        "products",
        sa.Column(
            "post_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Quantidade de vezes que foi postado"
        )
    )

    op.add_column(
        "products",
        sa.Column(
            "last_post_platform",
            sa.String(50),
            nullable=True,
            comment="Plataforma do ultimo post (instagram, tiktok, etc)"
        )
    )

    op.add_column(
        "products",
        sa.Column(
            "last_post_url",
            sa.String(500),
            nullable=True,
            comment="URL do ultimo post publicado"
        )
    )

    # Criar indice para queries eficientes de produtos nao postados recentemente
    op.create_index(
        "idx_products_last_post_date",
        "products",
        ["last_post_date"],
        unique=False
    )

    # Criar indice composto para a query de selecao de produtos para posting
    op.create_index(
        "idx_products_posting_selection",
        "products",
        ["availability", "post_count", "last_post_date"],
        unique=False
    )


def downgrade() -> None:
    """
    Remove os campos de controle de posts.
    """
    # Remover indices
    op.drop_index("idx_products_posting_selection", table_name="products")
    op.drop_index("idx_products_last_post_date", table_name="products")

    # Remover colunas
    op.drop_column("products", "last_post_url")
    op.drop_column("products", "last_post_platform")
    op.drop_column("products", "post_count")
    op.drop_column("products", "last_post_date")
