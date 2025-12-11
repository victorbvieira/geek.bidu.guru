"""
Dependencias de autenticacao para FastAPI.

Implementa:
- get_current_user: Extrai usuario do token JWT
- get_current_active_user: Verifica se usuario esta ativo
- require_role: Verifica se usuario tem role necessario
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_token
from app.database import get_db
from app.models import User
from app.models.user import UserRole
from app.repositories.user import UserRepository

# OAuth2 scheme - extrai token do header Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db=Depends(get_db),
) -> User:
    """
    Extrai e valida usuario do token JWT.

    Args:
        token: Token JWT do header Authorization
        db: Sessao do banco de dados

    Returns:
        Usuario autenticado

    Raises:
        HTTPException 401: Token invalido ou expirado
        HTTPException 404: Usuario nao encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verificar token
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Buscar usuario
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get(user_uuid)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Verifica se usuario esta ativo.

    Args:
        current_user: Usuario autenticado

    Returns:
        Usuario ativo

    Raises:
        HTTPException 403: Usuario inativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo",
        )
    return current_user


def require_role(*roles: UserRole):
    """
    Factory de dependencia que verifica se usuario tem um dos roles especificados.

    Uso:
        @router.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
        async def admin_only(): ...

        @router.get("/editors", dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.EDITOR))])
        async def admins_and_editors(): ...

    Args:
        *roles: Roles permitidos

    Returns:
        Dependencia FastAPI que verifica o role
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito. Roles permitidos: {[r.value for r in roles]}",
            )
        return current_user

    return role_checker


# Type aliases para usar em endpoints
CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_current_active_user)]
