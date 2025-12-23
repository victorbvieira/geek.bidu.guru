"""
Repositório para Integrações com Redes Sociais.

Fornece métodos específicos para:
- Busca por plataforma (Instagram, etc.)
- Atualização de tokens
- Verificação de credenciais
"""

from typing import Optional

from sqlalchemy import select

from app.models.social_integration import SocialIntegration, SocialPlatform
from app.repositories.base import BaseRepository


class SocialIntegrationRepository(BaseRepository[SocialIntegration]):
    """
    Repositório para gerenciamento de integrações sociais.

    Estende BaseRepository com métodos específicos para:
    - Buscar integração por plataforma
    - Atualizar tokens de acesso
    - Listar integrações ativas

    Exemplo de uso:
        repo = SocialIntegrationRepository(db)
        instagram = await repo.get_by_platform(SocialPlatform.INSTAGRAM)
        if instagram:
            print(f"IG User ID: {instagram.platform_user_id}")
    """

    def __init__(self, db):
        """
        Inicializa o repositório com o modelo SocialIntegration.

        Args:
            db: Sessão assíncrona do SQLAlchemy
        """
        super().__init__(SocialIntegration, db)

    async def get_by_platform(
        self,
        platform: SocialPlatform,
    ) -> Optional[SocialIntegration]:
        """
        Busca integração por plataforma.

        Como há apenas uma configuração por plataforma (índice único),
        este método retorna a configuração específica da plataforma.

        Args:
            platform: Plataforma social (ex: SocialPlatform.INSTAGRAM)

        Returns:
            Configuração da plataforma ou None se não existir

        Exemplo:
            instagram = await repo.get_by_platform(SocialPlatform.INSTAGRAM)
        """
        result = await self.db.execute(
            select(self.model).where(self.model.platform == platform)
        )
        return result.scalar_one_or_none()

    async def get_active_by_platform(
        self,
        platform: SocialPlatform,
    ) -> Optional[SocialIntegration]:
        """
        Busca integração ativa por plataforma.

        Similar a get_by_platform, mas filtra apenas integrações ativas.
        Útil para operações que requerem credenciais válidas.

        Args:
            platform: Plataforma social

        Returns:
            Configuração ativa da plataforma ou None

        Exemplo:
            ig = await repo.get_active_by_platform(SocialPlatform.INSTAGRAM)
            if ig and ig.has_credentials:
                # Pode fazer requisições à API do Instagram
                pass
        """
        result = await self.db.execute(
            select(self.model).where(
                self.model.platform == platform,
                self.model.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[SocialIntegration]:
        """
        Lista todas as integrações ativas.

        Útil para verificar quais integrações estão configuradas
        e prontas para uso.

        Returns:
            Lista de integrações ativas

        Exemplo:
            active = await repo.get_all_active()
            for integration in active:
                print(f"{integration.platform.value}: {integration.name}")
        """
        result = await self.db.execute(
            select(self.model)
            .where(self.model.is_active == True)  # noqa: E712
            .order_by(self.model.platform)
        )
        return list(result.scalars().all())

    async def update_token(
        self,
        platform: SocialPlatform,
        access_token: str,
    ) -> Optional[SocialIntegration]:
        """
        Atualiza apenas o token de acesso de uma plataforma.

        Método conveniente para renovação de tokens sem precisar
        buscar e atualizar manualmente a integração.

        Args:
            platform: Plataforma social
            access_token: Novo token de acesso

        Returns:
            Integração atualizada ou None se não encontrada

        Exemplo:
            updated = await repo.update_token(
                SocialPlatform.INSTAGRAM,
                "novo_token_aqui"
            )
        """
        integration = await self.get_by_platform(platform)
        if not integration:
            return None

        return await self.update(integration, {"access_token": access_token})

    async def update_credentials(
        self,
        platform: SocialPlatform,
        platform_user_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Optional[SocialIntegration]:
        """
        Atualiza credenciais (user_id e/ou token) de uma plataforma.

        Permite atualização parcial - apenas os campos fornecidos
        serão atualizados.

        Args:
            platform: Plataforma social
            platform_user_id: Novo ID do usuário (opcional)
            access_token: Novo token de acesso (opcional)

        Returns:
            Integração atualizada ou None se não encontrada

        Exemplo:
            # Atualizar ambos
            updated = await repo.update_credentials(
                SocialPlatform.INSTAGRAM,
                platform_user_id="17841400123456789",
                access_token="novo_token"
            )

            # Atualizar apenas o token
            updated = await repo.update_credentials(
                SocialPlatform.INSTAGRAM,
                access_token="novo_token"
            )
        """
        integration = await self.get_by_platform(platform)
        if not integration:
            return None

        update_data = {}
        if platform_user_id is not None:
            update_data["platform_user_id"] = platform_user_id
        if access_token is not None:
            update_data["access_token"] = access_token

        if not update_data:
            return integration  # Nada para atualizar

        return await self.update(integration, update_data)

    async def has_valid_credentials(self, platform: SocialPlatform) -> bool:
        """
        Verifica se uma plataforma tem credenciais válidas configuradas.

        Útil para verificar antes de tentar fazer operações que
        requerem autenticação com a API da plataforma.

        Args:
            platform: Plataforma social

        Returns:
            True se tiver user_id e token configurados, False caso contrário

        Exemplo:
            if await repo.has_valid_credentials(SocialPlatform.INSTAGRAM):
                # Pode fazer requisições à API do Instagram
                pass
        """
        integration = await self.get_active_by_platform(platform)
        return integration is not None and integration.has_credentials
