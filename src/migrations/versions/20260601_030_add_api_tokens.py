"""Add api_tokens table for long-lived API authentication.

Revision ID: 030
Revises: 029
Create Date: 2026-06-01

Cria a tabela api_tokens, que armazena tokens de API de longa duração
(formato `pcat_<32_hex>`) emitidos para usuários — principalmente os de
role `automation` que precisam autenticar agentes externos (paperclip) sem
depender do fluxo JWT login/refresh de 24h/7d.

Apenas o hash sha256 do token é armazenado. O valor completo é retornado
uma única vez na criação.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "030"
down_revision: Union[str, None] = "029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("token_prefix", sa.String(length=16), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("token_hash", name="uq_api_tokens_token_hash"),
    )
    op.create_index("idx_api_tokens_user", "api_tokens", ["user_id"])
    op.create_index("idx_api_tokens_hash", "api_tokens", ["token_hash"])
    op.create_index(
        "idx_api_tokens_active", "api_tokens", ["user_id", "revoked_at"]
    )


def downgrade() -> None:
    op.drop_index("idx_api_tokens_active", table_name="api_tokens")
    op.drop_index("idx_api_tokens_hash", table_name="api_tokens")
    op.drop_index("idx_api_tokens_user", table_name="api_tokens")
    op.drop_table("api_tokens")
