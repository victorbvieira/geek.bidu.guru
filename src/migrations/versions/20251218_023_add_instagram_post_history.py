"""
Adiciona tabela de histórico de publicações Instagram e campo last_ig_media_id.

Cria:
- Tabela instagram_post_history: Histórico detalhado de cada publicação
- Campo last_ig_media_id na tabela products: IG Media ID do último post

A tabela de histórico armazena informações de cada publicação individual,
permitindo rastrear múltiplas publicações do mesmo produto ao longo do tempo.

O campo last_ig_media_id no produto é uma denormalização para acesso rápido
ao ID da última publicação sem precisar consultar o histórico.

Revision ID: 023
Revises: 022
Create Date: 2025-12-18
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# Identificadores da migration
revision: str = "023"
down_revision: str = "022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Cria tabela instagram_post_history e adiciona campo last_ig_media_id.
    """
    # 1. Cria tabela de histórico de publicações Instagram
    op.create_table(
        "instagram_post_history",
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
            index=True,
            comment="UUID do produto publicado",
        ),
        sa.Column(
            "ig_media_id",
            sa.String(100),
            nullable=True,
            index=True,
            comment="ID da mídia retornado pela Graph API do Instagram",
        ),
        sa.Column(
            "post_url",
            sa.String(500),
            nullable=True,
            comment="URL do post no Instagram (permalink)",
        ),
        sa.Column(
            "caption",
            sa.Text(),
            nullable=True,
            comment="Caption utilizada na publicação",
        ),
        sa.Column(
            "posted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Data/hora da publicação no Instagram",
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

    # 2. Cria índices adicionais para a tabela de histórico
    op.create_index(
        "idx_instagram_posts_product_id",
        "instagram_post_history",
        ["product_id"],
    )
    op.create_index(
        "idx_instagram_posts_ig_media_id",
        "instagram_post_history",
        ["ig_media_id"],
    )
    op.create_index(
        "idx_instagram_posts_posted_at",
        "instagram_post_history",
        ["posted_at"],
    )

    # 3. Adiciona campo last_ig_media_id na tabela products
    op.add_column(
        "products",
        sa.Column(
            "last_ig_media_id",
            sa.String(100),
            nullable=True,
            comment="IG Media ID do ultimo post no Instagram (retornado pela Graph API)",
        ),
    )


def downgrade() -> None:
    """
    Remove tabela instagram_post_history e campo last_ig_media_id.
    """
    # 1. Remove campo last_ig_media_id da tabela products
    op.drop_column("products", "last_ig_media_id")

    # 2. Remove índices da tabela de histórico
    op.drop_index("idx_instagram_posts_posted_at", table_name="instagram_post_history")
    op.drop_index("idx_instagram_posts_ig_media_id", table_name="instagram_post_history")
    op.drop_index("idx_instagram_posts_product_id", table_name="instagram_post_history")

    # 3. Remove tabela de histórico
    op.drop_table("instagram_post_history")
