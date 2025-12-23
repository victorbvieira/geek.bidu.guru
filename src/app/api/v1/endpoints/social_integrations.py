"""
Endpoints REST para Integrações com Redes Sociais.

Este módulo implementa APIs para gerenciamento de configurações
de integração com redes sociais, começando pelo Instagram.

AUTENTICACAO:
    Todos os endpoints requerem autenticação JWT.
    Role obrigatório: ADMIN

Endpoints disponíveis:
    GET    /social-integrations               - Lista todas as integrações
    GET    /social-integrations/{id}          - Busca integração por ID
    GET    /social-integrations/platform/{p}  - Busca integração por plataforma
    PATCH  /social-integrations/{id}          - Atualiza integração
    PATCH  /social-integrations/{id}/token    - Atualiza apenas o token
    PATCH  /social-integrations/{id}/credentials - Atualiza credenciais

Segurança:
    - Apenas admins podem acessar estes endpoints
    - Token completo é retornado para uso em integrações (n8n, etc.)
"""

from datetime import datetime, UTC
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SocialIntegrationRepo
from app.core.deps import require_role
from app.models.social_integration import SocialPlatform
from app.models.user import UserRole
from app.schemas.social_integration import (
    SocialIntegrationBrief,
    SocialIntegrationResponse,
    SocialIntegrationTokenUpdateResponse,
    SocialIntegrationUpdate,
    SocialIntegrationUpdateCredentials,
    SocialIntegrationUpdateToken,
)

# Router com prefixo e tag para documentação OpenAPI
router = APIRouter(prefix="/social-integrations", tags=["social-integrations"])

# Apenas admins podem acessar configurações de integração
ALLOWED_ROLES = [UserRole.ADMIN]


# =============================================================================
# Helpers
# =============================================================================


def _to_response(integration) -> SocialIntegrationResponse:
    """
    Converte modelo para schema de resposta.

    Adiciona campos computados (has_credentials) e retorna
    o token completo para uso em integrações.
    """
    return SocialIntegrationResponse(
        id=integration.id,
        platform=integration.platform,
        name=integration.name,
        platform_user_id=integration.platform_user_id,
        access_token=integration.access_token,
        is_active=integration.is_active,
        has_credentials=integration.has_credentials,
        created_at=integration.created_at,
        updated_at=integration.updated_at,
    )


# =============================================================================
# Endpoints de Listagem
# =============================================================================


@router.get(
    "",
    response_model=list[SocialIntegrationBrief],
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def list_integrations(
    repo: SocialIntegrationRepo,
):
    """
    Lista todas as integrações de redes sociais.

    **Autenticação**: Requer token JWT com role ADMIN.

    Retorna uma lista resumida de todas as integrações cadastradas,
    sem expor dados sensíveis como tokens.

    Returns:
        Lista de SocialIntegrationBrief

    Raises:
        HTTPException 401: Token inválido ou ausente
        HTTPException 403: Role não autorizado
    """
    integrations = await repo.get_multi(order_by="platform", desc=False)

    return [
        SocialIntegrationBrief(
            id=i.id,
            platform=i.platform,
            name=i.name,
            is_active=i.is_active,
            has_credentials=i.has_credentials,
        )
        for i in integrations
    ]


@router.get(
    "/{integration_id}",
    response_model=SocialIntegrationResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def get_integration(
    integration_id: UUID,
    repo: SocialIntegrationRepo,
):
    """
    Busca integração por ID.

    **Autenticação**: Requer token JWT com role ADMIN.

    Retorna detalhes da integração, incluindo preview do token
    (nunca o token completo por segurança).

    Args:
        integration_id: UUID da integração

    Returns:
        SocialIntegrationResponse

    Raises:
        HTTPException 401: Token inválido ou ausente
        HTTPException 403: Role não autorizado
        HTTPException 404: Integração não encontrada
    """
    integration = await repo.get(integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integração não encontrada",
        )

    return _to_response(integration)


@router.get(
    "/platform/{platform}",
    response_model=SocialIntegrationResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def get_integration_by_platform(
    platform: SocialPlatform,
    repo: SocialIntegrationRepo,
):
    """
    Busca integração por plataforma.

    **Autenticação**: Requer token JWT com role ADMIN.

    Útil para buscar diretamente a configuração do Instagram
    sem precisar saber o UUID.

    Args:
        platform: Plataforma (instagram, etc.)

    Returns:
        SocialIntegrationResponse

    Raises:
        HTTPException 401: Token inválido ou ausente
        HTTPException 403: Role não autorizado
        HTTPException 404: Integração não encontrada
    """
    integration = await repo.get_by_platform(platform)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integração para {platform.value} não encontrada",
        )

    return _to_response(integration)


# =============================================================================
# Endpoints de Atualização
# =============================================================================


@router.patch(
    "/{integration_id}",
    response_model=SocialIntegrationResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def update_integration(
    integration_id: UUID,
    data: SocialIntegrationUpdate,
    repo: SocialIntegrationRepo,
):
    """
    Atualiza integração.

    **Autenticação**: Requer token JWT com role ADMIN.

    Permite atualização parcial - apenas campos fornecidos
    serão atualizados.

    Args:
        integration_id: UUID da integração
        data: Dados para atualização

    Returns:
        SocialIntegrationResponse atualizada

    Raises:
        HTTPException 401: Token inválido ou ausente
        HTTPException 403: Role não autorizado
        HTTPException 404: Integração não encontrada

    Body (JSON):
        {
            "name": "Nova Conta",           // opcional
            "platform_user_id": "1234...",  // opcional
            "access_token": "EAABc...",     // opcional
            "is_active": true               // opcional
        }
    """
    integration = await repo.get(integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integração não encontrada",
        )

    # Filtra apenas campos com valor (não None)
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        # Nenhum campo para atualizar
        return _to_response(integration)

    updated = await repo.update(integration, update_data)
    return _to_response(updated)


@router.patch(
    "/{integration_id}/token",
    response_model=SocialIntegrationTokenUpdateResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def update_integration_token(
    integration_id: UUID,
    data: SocialIntegrationUpdateToken,
    repo: SocialIntegrationRepo,
):
    """
    Atualiza apenas o token de acesso.

    **Autenticação**: Requer token JWT com role ADMIN.

    Endpoint específico para renovação de tokens, sem precisar
    enviar outros campos.

    Args:
        integration_id: UUID da integração
        data: Novo token

    Returns:
        SocialIntegrationTokenUpdateResponse confirmando atualização

    Raises:
        HTTPException 401: Token inválido ou ausente
        HTTPException 403: Role não autorizado
        HTTPException 404: Integração não encontrada

    Body (JSON):
        {
            "access_token": "EAABcDefGhI..."
        }
    """
    integration = await repo.get(integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integração não encontrada",
        )

    updated = await repo.update(integration, {"access_token": data.access_token})

    return SocialIntegrationTokenUpdateResponse(
        success=True,
        message="Token atualizado com sucesso",
        updated_at=updated.updated_at,
    )


@router.patch(
    "/{integration_id}/credentials",
    response_model=SocialIntegrationResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def update_integration_credentials(
    integration_id: UUID,
    data: SocialIntegrationUpdateCredentials,
    repo: SocialIntegrationRepo,
):
    """
    Atualiza credenciais (user_id e/ou token).

    **Autenticação**: Requer token JWT com role ADMIN.

    Endpoint para atualização das credenciais de API.
    Pelo menos um campo deve ser fornecido.

    Args:
        integration_id: UUID da integração
        data: Credenciais para atualização

    Returns:
        SocialIntegrationResponse atualizada

    Raises:
        HTTPException 400: Nenhuma credencial fornecida
        HTTPException 401: Token inválido ou ausente
        HTTPException 403: Role não autorizado
        HTTPException 404: Integração não encontrada

    Body (JSON):
        {
            "platform_user_id": "17841400123...",  // opcional
            "access_token": "EAABcDefGhI..."       // opcional
        }
    """
    # Valida que pelo menos um campo foi fornecido
    if not data.platform_user_id and not data.access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pelo menos platform_user_id ou access_token deve ser fornecido",
        )

    integration = await repo.get(integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integração não encontrada",
        )

    # Monta dados de atualização (apenas campos fornecidos)
    update_data = {}
    if data.platform_user_id is not None:
        update_data["platform_user_id"] = data.platform_user_id
    if data.access_token is not None:
        update_data["access_token"] = data.access_token

    updated = await repo.update(integration, update_data)
    return _to_response(updated)
