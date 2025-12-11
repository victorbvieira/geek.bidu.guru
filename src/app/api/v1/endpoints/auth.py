"""
Endpoints de autenticacao.

Rotas:
- POST /auth/login - Login com email/senha
- POST /auth/refresh - Renovar tokens com refresh token
- GET /auth/me - Dados do usuario autenticado
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import ActiveUser
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from app.database import get_db
from app.repositories.user import UserRepository
from app.schemas import RefreshTokenRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login com email e senha",
    description="Autentica usuario e retorna tokens JWT (access e refresh).",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db),
):
    """
    Login com credenciais (email/senha).

    Retorna:
    - access_token: Token de acesso (expira em 30 minutos por padrao)
    - refresh_token: Token de renovacao (expira em 7 dias por padrao)

    Uso do access_token:
    ```
    Authorization: Bearer <access_token>
    ```
    """
    repo = UserRepository(db)

    # Buscar usuario por email
    user = await repo.get_by_email(form_data.username)  # OAuth2 usa 'username'

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar senha
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar se usuario esta ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo",
        )

    # Gerar tokens
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value},
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar tokens",
    description="Usa refresh token para obter novos tokens JWT.",
)
async def refresh_tokens(
    request: RefreshTokenRequest,
    db=Depends(get_db),
):
    """
    Renova tokens usando refresh token.

    Use quando o access_token expirar para obter novos tokens
    sem necessidade de fazer login novamente.
    """
    # Verificar refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar usuario para verificar se ainda esta ativo
    repo = UserRepository(db)
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await repo.get(user_uuid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo",
        )

    # Gerar novos tokens
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value},
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Dados do usuario autenticado",
    description="Retorna dados do usuario autenticado pelo token JWT.",
)
async def get_current_user_data(
    current_user: ActiveUser,
):
    """
    Retorna dados do usuario autenticado.

    Requer header Authorization com token valido.
    """
    return current_user
