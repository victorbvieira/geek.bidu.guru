"""
FIX: Recria tabela social_integrations.

Esta migration corrige problemas de execução parcial da migration anterior.
Remove e recria o enum e a tabela de forma idempotente.

Revision ID: 025a
Revises: 025
Create Date: 2025-12-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# Identificadores da migration
revision: str = "025a"
down_revision: str = "025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Limpa e recria a estrutura de social_integrations.
    """
    conn = op.get_bind()

    # 1. Remove tabela se existir (com CASCADE para remover dependências)
    op.execute("DROP TABLE IF EXISTS social_integrations CASCADE")

    # 2. Remove enum se existir
    op.execute("DROP TYPE IF EXISTS social_platform CASCADE")

    # 3. Cria enum novamente
    op.execute("CREATE TYPE social_platform AS ENUM ('instagram')")

    # 4. Cria tabela
    op.execute("""
        CREATE TABLE social_integrations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            platform social_platform NOT NULL,
            name VARCHAR(100) NOT NULL DEFAULT 'Conta Principal',
            platform_user_id VARCHAR(100),
            access_token TEXT,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)

    # 5. Cria índices
    op.execute("""
        CREATE UNIQUE INDEX idx_social_integrations_platform
        ON social_integrations (platform)
    """)
    op.execute("""
        CREATE INDEX idx_social_integrations_active
        ON social_integrations (is_active)
    """)

    # 6. Adiciona comentários nas colunas
    op.execute("""
        COMMENT ON COLUMN social_integrations.platform IS
        'Plataforma de rede social (instagram, etc.)'
    """)
    op.execute("""
        COMMENT ON COLUMN social_integrations.name IS
        'Nome identificador da integração'
    """)
    op.execute("""
        COMMENT ON COLUMN social_integrations.platform_user_id IS
        'ID do usuário na plataforma (ex: IG_USER_ID)'
    """)
    op.execute("""
        COMMENT ON COLUMN social_integrations.access_token IS
        'Token de acesso à API'
    """)
    op.execute("""
        COMMENT ON COLUMN social_integrations.is_active IS
        'Se a integração está ativa e pode ser usada'
    """)

    # 7. Insere registro inicial do Instagram
    op.execute("""
        INSERT INTO social_integrations (platform, name, is_active)
        VALUES ('instagram', 'Instagram Principal', true)
    """)


def downgrade() -> None:
    """
    Remove tabela e enum.
    """
    op.execute("DROP TABLE IF EXISTS social_integrations CASCADE")
    op.execute("DROP TYPE IF EXISTS social_platform CASCADE")
