"""
Adiciona campos de verificacao de email na newsletter.

Implementa double opt-in para newsletter:
- email_verified: indica se o email foi confirmado
- verification_token: token para link de confirmacao
- verification_sent_at: quando o email de verificacao foi enviado
- verified_at: quando o usuario confirmou o email

Revision ID: 027
Revises: 026
Create Date: 2025-12-24
"""

from alembic import op
import sqlalchemy as sa


# Identificadores da migration
revision: str = "027"
down_revision: str = "026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Adiciona campos de verificacao de email na tabela newsletter_signups.
    """
    # Campo para indicar se email foi verificado
    op.add_column(
        "newsletter_signups",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="Se o email foi verificado via double opt-in",
        ),
    )

    # Token para verificacao de email
    op.add_column(
        "newsletter_signups",
        sa.Column(
            "verification_token",
            sa.String(64),
            nullable=True,
            comment="Token para link de verificacao de email",
        ),
    )

    # Quando o email de verificacao foi enviado
    op.add_column(
        "newsletter_signups",
        sa.Column(
            "verification_sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Data/hora do envio do email de verificacao",
        ),
    )

    # Quando o usuario verificou o email
    op.add_column(
        "newsletter_signups",
        sa.Column(
            "verified_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Data/hora da verificacao do email",
        ),
    )

    # Indice para busca por token (usado na confirmacao)
    op.create_index(
        "idx_newsletter_verification_token",
        "newsletter_signups",
        ["verification_token"],
    )

    # Indice para filtrar por verificados
    op.create_index(
        "idx_newsletter_verified",
        "newsletter_signups",
        ["email_verified"],
    )


def downgrade() -> None:
    """
    Remove campos de verificacao de email.
    """
    # Remove indices
    op.drop_index("idx_newsletter_verified", table_name="newsletter_signups")
    op.drop_index("idx_newsletter_verification_token", table_name="newsletter_signups")

    # Remove colunas
    op.drop_column("newsletter_signups", "verified_at")
    op.drop_column("newsletter_signups", "verification_sent_at")
    op.drop_column("newsletter_signups", "verification_token")
    op.drop_column("newsletter_signups", "email_verified")
