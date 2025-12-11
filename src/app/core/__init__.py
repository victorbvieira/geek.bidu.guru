"""
Modulo core com utilitarios centrais da aplicacao.
"""

from app.core.deps import (
    ActiveUser,
    CurrentUser,
    get_current_active_user,
    get_current_user,
    require_role,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)

__all__ = [
    # Security
    "create_access_token",
    "create_refresh_token",
    "get_password_hash",
    "verify_password",
    "verify_token",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "CurrentUser",
    "ActiveUser",
]
