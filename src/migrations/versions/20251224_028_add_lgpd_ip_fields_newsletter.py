"""
Adiciona campos de IP para compliance LGPD na newsletter.

Para atender os requisitos da LGPD, armazenamos:
- signup_ip: IP do usuario no momento da inscricao
- consent_ip: IP do usuario no momento do consentimento (click no email)

Esses dados comprovam que o usuario deu consentimento explicito
para receber a newsletter.

Revision ID: 028
Revises: 027
Create Date: 2025-12-24
"""

from alembic import op
import sqlalchemy as sa


# Identificadores da migration
revision: str = "028"
down_revision: str = "027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Adiciona campos de IP para rastreabilidade LGPD.
    """
    # IP do usuario no momento da inscricao
    op.add_column(
        "newsletter_signups",
        sa.Column(
            "signup_ip",
            sa.String(45),  # Suporta IPv6
            nullable=True,
            comment="IP do usuario no momento da inscricao (LGPD)",
        ),
    )

    # IP do usuario no momento do consentimento (click no email de verificacao)
    op.add_column(
        "newsletter_signups",
        sa.Column(
            "consent_ip",
            sa.String(45),  # Suporta IPv6
            nullable=True,
            comment="IP do usuario ao confirmar email - prova de consentimento (LGPD)",
        ),
    )


def downgrade() -> None:
    """
    Remove campos de IP LGPD.
    """
    op.drop_column("newsletter_signups", "consent_ip")
    op.drop_column("newsletter_signups", "signup_ip")
