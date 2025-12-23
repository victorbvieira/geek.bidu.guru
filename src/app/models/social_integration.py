"""
Modelo de Integração com Redes Sociais.

Armazena configurações de API para integrações com redes sociais,
começando pelo Instagram (IG_USER_ID e access token).

Este modelo é projetado para ser extensível, permitindo adicionar
outras redes sociais no futuro (Facebook, TikTok, etc.).
"""

import enum
from typing import Optional

from sqlalchemy import Boolean, Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class SocialPlatform(str, enum.Enum):
    """Plataformas de redes sociais suportadas."""

    INSTAGRAM = "instagram"
    # Futuras plataformas:
    # FACEBOOK = "facebook"
    # TIKTOK = "tiktok"
    # TWITTER = "twitter"


class SocialIntegration(Base, UUIDMixin, TimestampMixin):
    """
    Configuração de integração com redes sociais.

    Armazena credenciais e configurações de API para cada plataforma.
    Por segurança, os tokens são armazenados de forma criptografada
    (recomendação para produção) ou ofuscados.

    Atributos:
        id: UUID primary key
        platform: Plataforma social (instagram, etc.)
        name: Nome identificador da integração (ex: "Conta Principal")
        platform_user_id: ID do usuário na plataforma (ex: IG_USER_ID)
        access_token: Token de acesso à API da plataforma
        is_active: Se a integração está ativa
        created_at: Data de criação
        updated_at: Data de atualização

    Exemplo de uso:
        # Buscar integração do Instagram
        ig_config = await repo.get_by_platform(SocialPlatform.INSTAGRAM)
        if ig_config:
            user_id = ig_config.platform_user_id
            token = ig_config.access_token
    """

    __tablename__ = "social_integrations"

    # Identificação da plataforma
    platform: Mapped[SocialPlatform] = mapped_column(
        Enum(
            SocialPlatform,
            name="social_platform",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        comment="Plataforma de rede social (instagram, etc.)",
    )

    # Nome amigável para identificação (útil se houver múltiplas contas)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Conta Principal",
        comment="Nome identificador da integração",
    )

    # ID do usuário na plataforma (ex: IG_USER_ID para Instagram)
    platform_user_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="ID do usuário na plataforma (ex: IG_USER_ID)",
    )

    # Token de acesso à API da plataforma
    # IMPORTANTE: Em produção, considerar criptografar este campo
    access_token: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        comment="Token de acesso à API (armazenado de forma segura)",
    )

    # Status da integração
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Se a integração está ativa e pode ser usada",
    )

    # Índices para consultas frequentes
    __table_args__ = (
        # Índice único por plataforma (apenas uma configuração por plataforma ativa)
        # Se precisar de múltiplas contas, remover unique=True
        Index("idx_social_integrations_platform", "platform", unique=True),
        Index("idx_social_integrations_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<SocialIntegration {self.platform.value}: {self.name}>"

    @property
    def has_credentials(self) -> bool:
        """Verifica se as credenciais estão configuradas."""
        return bool(self.platform_user_id and self.access_token)

    @property
    def token_preview(self) -> str:
        """Retorna preview ofuscado do token para exibição."""
        if not self.access_token:
            return ""
        # Mostra apenas os primeiros e últimos caracteres
        token = self.access_token
        if len(token) > 20:
            return f"{token[:8]}...{token[-4:]}"
        return "***"
