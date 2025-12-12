"""Seed automation user for n8n integration.

Revision ID: 004
Revises: 003
Create Date: 2025-12-12

Creates the automation user used by n8n to create posts and products.
This user cannot log in via the web interface (no password).
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Password hash impossivel de fazer login (placeholder)
# Este usuario autentica via API Key, nao via senha
AUTOMATION_PASSWORD_HASH = "$2b$12$INVALID_HASH_NO_LOGIN_ALLOWED_VIA_PASSWORD"


def upgrade() -> None:
    """Create automation user for n8n."""
    op.execute(f"""
        INSERT INTO users (id, name, email, password_hash, role, is_active, created_at, updated_at)
        VALUES (
            gen_random_uuid(),
            'n8n Automation',
            'automation@geek.bidu.guru',
            '{AUTOMATION_PASSWORD_HASH}',
            'automation',
            true,
            NOW(),
            NOW()
        )
        ON CONFLICT (email) DO NOTHING;
    """)


def downgrade() -> None:
    """Remove automation user."""
    op.execute("""
        DELETE FROM users WHERE email = 'automation@geek.bidu.guru';
    """)
