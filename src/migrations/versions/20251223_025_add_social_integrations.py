"""
Adiciona tabela de integrações com redes sociais.

Cria:
- ENUM social_platform: Tipos de plataformas suportadas (instagram, etc.)
- Tabela social_integrations: Configurações de API por plataforma

Esta tabela armazena credenciais de acesso às APIs de redes sociais,
começando pelo Instagram (IG_USER_ID e access token).

Revision ID: 025
Revises: 024c
Create Date: 2025-12-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM


# Identificadores da migration
revision: str = "025"
down_revision: str = "024c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Cria ENUM social_platform e tabela social_integrations.
    """
    # Verifica se o ENUM já existe antes de criar
    # (caso a migration tenha falhado parcialmente antes)
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'social_platform'")
    )
    enum_exists = result.fetchone() is not None

    if not enum_exists:
        # Cria ENUM manualmente via SQL para evitar problemas com asyncpg
        op.execute("CREATE TYPE social_platform AS ENUM ('instagram')")

    # Verifica se a tabela já existe
    result = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'social_integrations'"
        )
    )
    table_exists = result.fetchone() is not None

    if not table_exists:
        # Cria tabela de integrações sociais
        op.create_table(
            "social_integrations",
            # Primary key UUID
            sa.Column(
                "id",
                UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            # Plataforma (instagram, etc.) - usa ENUM já existente
            sa.Column(
                "platform",
                ENUM("instagram", name="social_platform", create_type=False),
                nullable=False,
                comment="Plataforma de rede social (instagram, etc.)",
            ),
            # Nome identificador da integração
            sa.Column(
                "name",
                sa.String(100),
                nullable=False,
                server_default="Conta Principal",
                comment="Nome identificador da integração",
            ),
            # ID do usuário na plataforma (ex: IG_USER_ID)
            sa.Column(
                "platform_user_id",
                sa.String(100),
                nullable=True,
                comment="ID do usuário na plataforma (ex: IG_USER_ID)",
            ),
            # Token de acesso à API
            sa.Column(
                "access_token",
                sa.Text(),
                nullable=True,
                comment="Token de acesso à API (armazenado de forma segura)",
            ),
            # Status da integração
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
                comment="Se a integração está ativa e pode ser usada",
            ),
            # Timestamps
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

        # Cria índices
        op.create_index(
            "idx_social_integrations_platform",
            "social_integrations",
            ["platform"],
            unique=True,
        )
        op.create_index(
            "idx_social_integrations_active",
            "social_integrations",
            ["is_active"],
        )

        # Insere configuração inicial do Instagram
        op.execute(
            """
            INSERT INTO social_integrations (platform, name, is_active)
            VALUES ('instagram', 'Instagram Principal', true)
            """
        )


def downgrade() -> None:
    """
    Remove tabela social_integrations e ENUM social_platform.
    """
    # Remove índices
    op.drop_index("idx_social_integrations_active", table_name="social_integrations")
    op.drop_index("idx_social_integrations_platform", table_name="social_integrations")

    # Remove tabela
    op.drop_table("social_integrations")

    # Remove ENUM
    op.execute("DROP TYPE IF EXISTS social_platform")
