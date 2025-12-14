"""
Repositorio para configuracoes de IA.

Fornece acesso a dados de configuracao de providers, modelos e prompts
para cada caso de uso de IA no sistema.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_config import AIConfig, AIUseCase
from app.repositories.base import BaseRepository


class AIConfigRepository(BaseRepository[AIConfig]):
    """
    Repositorio para operacoes com configuracoes de IA.

    Alem das operacoes CRUD base, fornece metodos especificos
    para busca por caso de uso e listagem de configs ativas.
    """

    def __init__(self, db: AsyncSession):
        """Inicializa o repositorio com o modelo AIConfig."""
        super().__init__(AIConfig, db)

    async def get_by_use_case(self, use_case: AIUseCase) -> AIConfig | None:
        """
        Busca configuracao por caso de uso.

        Args:
            use_case: Enum do caso de uso (ex: AIUseCase.SEO_TITLE)

        Returns:
            Configuracao encontrada ou None
        """
        result = await self.db.execute(
            select(self.model).where(self.model.use_case == use_case)
        )
        return result.scalar_one_or_none()

    async def get_active_by_use_case(self, use_case: AIUseCase) -> AIConfig | None:
        """
        Busca configuracao ativa por caso de uso.

        Args:
            use_case: Enum do caso de uso

        Returns:
            Configuracao ativa encontrada ou None
        """
        result = await self.db.execute(
            select(self.model).where(
                self.model.use_case == use_case,
                self.model.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[AIConfig]:
        """
        Retorna todas as configuracoes ordenadas por nome.

        Returns:
            Lista de todas as configuracoes
        """
        result = await self.db.execute(
            select(self.model).order_by(self.model.name)
        )
        return list(result.scalars().all())

    async def get_all_active(self) -> list[AIConfig]:
        """
        Retorna todas as configuracoes ativas.

        Returns:
            Lista de configuracoes ativas
        """
        result = await self.db.execute(
            select(self.model)
            .where(self.model.is_active == True)  # noqa: E712
            .order_by(self.model.name)
        )
        return list(result.scalars().all())

    async def search(
        self,
        query: str,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AIConfig]:
        """
        Busca configuracoes por nome ou descricao.

        Args:
            query: Termo de busca
            skip: Registros a pular
            limit: Maximo de registros

        Returns:
            Lista de configuracoes que correspondem a busca
        """
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(self.model)
            .where(
                (self.model.name.ilike(search_term))
                | (self.model.description.ilike(search_term))
            )
            .order_by(self.model.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_search(self, query: str) -> int:
        """
        Conta configuracoes que correspondem a busca.

        Args:
            query: Termo de busca

        Returns:
            Numero de configuracoes encontradas
        """
        from sqlalchemy import func

        search_term = f"%{query}%"
        result = await self.db.execute(
            select(func.count())
            .select_from(self.model)
            .where(
                (self.model.name.ilike(search_term))
                | (self.model.description.ilike(search_term))
            )
        )
        return result.scalar_one()
