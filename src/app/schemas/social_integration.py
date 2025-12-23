"""
Schemas Pydantic para Integração com Redes Sociais.

Define schemas para:
- Leitura de configurações (sem expor token completo)
- Atualização de credenciais (IG_USER_ID e token)
- Resposta da API com dados seguros
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.social_integration import SocialPlatform
from app.schemas.base import BaseSchema, ResponseSchema


# =============================================================================
# Schemas Base
# =============================================================================


class SocialIntegrationBase(BaseSchema):
    """
    Campos base de integração social.

    Contém apenas informações não sensíveis que podem ser
    exibidas livremente na interface.
    """

    platform: SocialPlatform = Field(
        ...,
        description="Plataforma de rede social",
        examples=["instagram"],
    )
    name: str = Field(
        ...,
        max_length=100,
        description="Nome identificador da integração",
        examples=["Instagram Principal"],
    )
    is_active: bool = Field(
        default=True,
        description="Se a integração está ativa",
    )


# =============================================================================
# Schemas de Criação/Atualização
# =============================================================================


class SocialIntegrationCreate(SocialIntegrationBase):
    """
    Schema para criação de nova integração.

    Inclui credenciais que serão armazenadas no banco.
    """

    platform_user_id: Optional[str] = Field(
        None,
        max_length=100,
        description="ID do usuário na plataforma (ex: IG_USER_ID)",
        examples=["17841400123456789"],
    )
    access_token: Optional[str] = Field(
        None,
        description="Token de acesso à API da plataforma",
    )


class SocialIntegrationUpdate(BaseSchema):
    """
    Schema para atualização de integração existente.

    Todos os campos são opcionais para permitir atualização parcial.
    """

    name: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome identificador da integração",
    )
    platform_user_id: Optional[str] = Field(
        None,
        max_length=100,
        description="ID do usuário na plataforma",
    )
    access_token: Optional[str] = Field(
        None,
        description="Token de acesso à API",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Se a integração está ativa",
    )


class SocialIntegrationUpdateToken(BaseSchema):
    """
    Schema específico para atualização apenas do token.

    Usado pelo endpoint PATCH /api/v1/social-integrations/{id}/token
    """

    access_token: str = Field(
        ...,
        min_length=1,
        description="Novo token de acesso à API",
    )


class SocialIntegrationUpdateCredentials(BaseSchema):
    """
    Schema para atualização de credenciais (user_id e token).

    Usado para atualizar ambas as credenciais de uma vez.
    """

    platform_user_id: Optional[str] = Field(
        None,
        max_length=100,
        description="ID do usuário na plataforma",
        examples=["17841400123456789"],
    )
    access_token: Optional[str] = Field(
        None,
        description="Novo token de acesso à API",
    )


# =============================================================================
# Schemas de Resposta
# =============================================================================


class SocialIntegrationResponse(ResponseSchema):
    """
    Schema de resposta completa com todos os dados.

    Inclui o token de acesso completo para uso em integrações.
    Apenas admins autenticados têm acesso a este endpoint.
    """

    platform: SocialPlatform
    name: str
    platform_user_id: Optional[str] = None
    access_token: Optional[str] = Field(
        None,
        description="Token de acesso à API (completo)",
    )
    is_active: bool
    has_credentials: bool = Field(
        ...,
        description="Indica se as credenciais estão configuradas",
    )


class SocialIntegrationBrief(BaseSchema):
    """
    Schema resumido para listagens.

    Contém apenas informações essenciais para exibição em listas.
    """

    id: UUID
    platform: SocialPlatform
    name: str
    is_active: bool
    has_credentials: bool


class SocialIntegrationDetail(SocialIntegrationResponse):
    """
    Schema detalhado para view de edição no admin.

    Adiciona informações extras úteis para administração.
    """

    created_at: datetime
    updated_at: datetime


# =============================================================================
# Schemas de Mensagem
# =============================================================================


class SocialIntegrationTokenUpdateResponse(BaseSchema):
    """Resposta após atualização de token."""

    success: bool = True
    message: str = Field(
        default="Token atualizado com sucesso",
        description="Mensagem de confirmação",
    )
    updated_at: datetime = Field(
        ...,
        description="Data/hora da atualização",
    )
