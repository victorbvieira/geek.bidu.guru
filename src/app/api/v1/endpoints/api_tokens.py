"""
Endpoints REST para gerenciamento de API Tokens.

Estes tokens (formato `pcat_<32_hex>`) são alternativos ao JWT login/refresh
para autenticação de longa duração — caso típico: agentes paperclip, n8n,
scripts CRON. São scoped a um usuário (especialmente `automation`).

Endpoints:
    POST   /users/{user_id}/api-tokens         - cria token (retorna valor UMA vez)
    GET    /users/{user_id}/api-tokens         - lista tokens (sem secrets)
    DELETE /users/{user_id}/api-tokens/{id}    - revoga (soft)

Segurança:
- Apenas o próprio user OU um admin pode gerar/listar/revogar tokens.
- O valor completo do token é retornado APENAS na resposta do POST.
- Após criado, só sobra hash + prefix. Perdeu o valor? Revoga e cria outro.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import ApiTokenRepo, UserRepo
from app.core.deps import ActiveUser
from app.models.user import UserRole
from app.schemas import (
    ApiTokenCreate,
    ApiTokenList,
    ApiTokenResponse,
    ApiTokenWithSecret,
    MessageResponse,
)
from app.services.api_token import create_api_token
from datetime import datetime, timezone

router = APIRouter(prefix="/users/{user_id}/api-tokens", tags=["api-tokens"])


def _ensure_can_manage(current_user, target_user_id: UUID) -> None:
    """Permite gerenciar tokens apenas do próprio user OU se for admin."""
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.id == target_user_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso restrito. Apenas admins ou o próprio usuário podem gerenciar tokens.",
    )


@router.post(
    "",
    response_model=ApiTokenWithSecret,
    status_code=status.HTTP_201_CREATED,
    summary="Gera novo API token (retorna valor uma única vez)",
)
async def create_token(
    user_id: UUID,
    data: ApiTokenCreate,
    current_user: ActiveUser,
    user_repo: UserRepo,
    token_repo: ApiTokenRepo,
) -> ApiTokenWithSecret:
    _ensure_can_manage(current_user, user_id)

    user = await user_repo.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    generated = await create_api_token(
        token_repo,
        user_id=user_id,
        name=data.name,
        expires_in_days=data.expires_in_days,
        created_by_user_id=current_user.id,
    )

    return ApiTokenWithSecret(
        id=generated.record.id,
        user_id=generated.record.user_id,
        name=generated.record.name,
        token_prefix=generated.record.token_prefix,
        expires_at=generated.record.expires_at,
        last_used_at=generated.record.last_used_at,
        revoked_at=generated.record.revoked_at,
        created_at=generated.record.created_at,
        created_by_user_id=generated.record.created_by_user_id,
        token=generated.token,
    )


@router.get(
    "",
    response_model=ApiTokenList,
    summary="Lista tokens do usuário (sem valores secretos)",
)
async def list_tokens(
    user_id: UUID,
    current_user: ActiveUser,
    token_repo: ApiTokenRepo,
    include_revoked: bool = False,
) -> ApiTokenList:
    _ensure_can_manage(current_user, user_id)
    items = await token_repo.list_by_user(user_id, include_revoked=include_revoked)
    return ApiTokenList(
        items=[ApiTokenResponse.model_validate(item) for item in items],
        total=len(items),
    )


@router.delete(
    "/{token_id}",
    response_model=MessageResponse,
    summary="Revoga token (soft delete, mantém audit trail)",
)
async def revoke_token(
    user_id: UUID,
    token_id: UUID,
    current_user: ActiveUser,
    token_repo: ApiTokenRepo,
) -> MessageResponse:
    _ensure_can_manage(current_user, user_id)

    record = await token_repo.get(token_id)
    if record is None or record.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token não encontrado",
        )
    if record.revoked_at is not None:
        return MessageResponse(message="Token já estava revogado.")

    changed = await token_repo.revoke(token_id, datetime.now(timezone.utc))
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao revogar token",
        )
    return MessageResponse(message="Token revogado com sucesso.")
