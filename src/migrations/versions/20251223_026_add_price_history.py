"""
Adiciona tabela de historico de precos.

Cria a tabela price_history para rastrear alteracoes de preco dos produtos,
permitindo analise de variacao, identificacao de promocoes e alertas.

Revision ID: 026
Revises: 025a
Create Date: 2025-12-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# Identificadores da migration
revision: str = "026"
down_revision: str = "025a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Cria tabela price_history com indices para consultas frequentes.
    """
    # Cria tabela de historico de precos
    op.create_table(
        "price_history",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "product_id",
            UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
            comment="UUID do produto relacionado",
        ),
        sa.Column(
            "price",
            sa.Numeric(10, 2),
            nullable=False,
            comment="Preco registrado neste momento",
        ),
        sa.Column(
            "previous_price",
            sa.Numeric(10, 2),
            nullable=True,
            comment="Preco anterior para calcular variacao",
        ),
        sa.Column(
            "currency",
            sa.String(3),
            nullable=False,
            server_default="BRL",
            comment="Moeda do preco (sempre BRL)",
        ),
        sa.Column(
            "source",
            sa.String(50),
            nullable=False,
            server_default="manual",
            comment="Fonte da atualizacao: manual, api_amazon, api_ml, scraper, etc",
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
            comment="Observacoes sobre a alteracao de preco",
        ),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Data/hora em que o preco foi registrado",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Cria indices para consultas frequentes
    op.create_index(
        "idx_price_history_product_id",
        "price_history",
        ["product_id"],
    )
    op.create_index(
        "idx_price_history_recorded_at",
        "price_history",
        ["recorded_at"],
    )
    op.create_index(
        "idx_price_history_product_recorded",
        "price_history",
        ["product_id", "recorded_at"],
    )


def downgrade() -> None:
    """
    Remove tabela price_history e seus indices.
    """
    # Remove indices
    op.drop_index("idx_price_history_product_recorded", table_name="price_history")
    op.drop_index("idx_price_history_recorded_at", table_name="price_history")
    op.drop_index("idx_price_history_product_id", table_name="price_history")

    # Remove tabela
    op.drop_table("price_history")
