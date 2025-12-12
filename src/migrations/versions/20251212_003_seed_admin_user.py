"""Seed admin user for initial access.

Revision ID: 003
Revises: 002
Create Date: 2025-12-12

Creates the initial admin user for production access.
Password should be changed after first login.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Password hash for "Admin@123" - CHANGE AFTER FIRST LOGIN!
# Generated with: bcrypt.hashpw("Admin@123".encode(), bcrypt.gensalt()).decode()
ADMIN_PASSWORD_HASH = "$2b$12$HMeTFJrvoD/HmG6YjCjtlekrFAyn0oUG/R.7Kml95FS9/y4E/WOgy"


def upgrade() -> None:
    """Create initial admin user."""
    op.execute(f"""
        INSERT INTO users (id, name, email, password_hash, role, is_active, created_at, updated_at)
        VALUES (
            gen_random_uuid(),
            'Administrador',
            'admin@geek.bidu.guru',
            '{ADMIN_PASSWORD_HASH}',
            'admin',
            true,
            NOW(),
            NOW()
        )
        ON CONFLICT (email) DO NOTHING;
    """)


def downgrade() -> None:
    """Remove initial admin user."""
    op.execute("""
        DELETE FROM users WHERE email = 'admin@geek.bidu.guru';
    """)
