"""
Repositório base com operações CRUD genéricas.

Este módulo implementa o padrão Repository combinado com Generics do Python
para criar uma camada de abstração entre a lógica de negócio e o acesso a dados.

Princípios SOLID aplicados:
    - Single Responsibility: Cada método tem uma única responsabilidade (CRUD)
    - Open/Closed: Classe base pode ser estendida sem modificação
    - Liskov Substitution: Repositórios específicos podem substituir o base
    - Dependency Inversion: Depende de abstrações (AsyncSession, Base)

Padrões utilizados:
    - Repository Pattern: Encapsula lógica de acesso a dados
    - Generic Repository: Reutilização através de TypeVar
    - Unit of Work: Integrado via AsyncSession do SQLAlchemy

Exemplo de uso:
    class UserRepository(BaseRepository[User]):
        def __init__(self, db: AsyncSession):
            super().__init__(User, db)

        async def get_by_email(self, email: str) -> User | None:
            return await self.get_by_field("email", email)
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

# TypeVar genérico vinculado ao Base do SQLAlchemy
# Permite type hints corretos em repositórios específicos
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repositório base genérico com operações CRUD assíncronas.

    Fornece implementação padrão para operações comuns de banco de dados,
    eliminando código duplicado nos repositórios específicos.

    Atributos:
        model (type[ModelType]): Classe do modelo SQLAlchemy
        db (AsyncSession): Sessão assíncrona do SQLAlchemy

    Type Parameters:
        ModelType: Tipo do modelo SQLAlchemy (deve herdar de Base)
    """

    def __init__(self, model: type[ModelType], db: AsyncSession):
        """
        Inicializa o repositório com o modelo e sessão do banco.

        Args:
            model: Classe do modelo SQLAlchemy (ex: User, Post)
            db: Sessão assíncrona do SQLAlchemy injetada via dependência
        """
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> ModelType | None:
        """
        Busca um registro por seu ID (UUID).

        Args:
            id: UUID do registro a ser buscado

        Returns:
            Instância do modelo se encontrado, None caso contrário

        Exemplo:
            user = await repo.get(uuid.UUID("..."))
            if user:
                print(user.name)
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_field(self, field: str, value: Any) -> ModelType | None:
        """
        Busca um registro por um campo específico.

        Método utilitário para buscas por campos únicos como email, slug, etc.
        Para buscas que podem retornar múltiplos registros, use get_multi.

        Args:
            field: Nome do campo/coluna do modelo
            value: Valor a ser buscado

        Returns:
            Primeira instância encontrada ou None

        Raises:
            AttributeError: Se o campo não existir no modelo

        Exemplo:
            user = await repo.get_by_field("email", "user@example.com")
        """
        column = getattr(self.model, field)
        result = await self.db.execute(
            select(self.model).where(column == value)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        desc: bool = True,
    ) -> list[ModelType]:
        """
        Lista registros com paginação e ordenação.

        Implementa paginação offset-based, adequada para conjuntos de dados
        de tamanho moderado. Para grandes volumes, considere cursor-based pagination.

        Args:
            skip: Número de registros a pular (offset). Default: 0
            limit: Número máximo de registros a retornar. Default: 100
            order_by: Nome do campo para ordenação. Default: None (ordem do banco)
            desc: Se True, ordena decrescente; se False, crescente. Default: True

        Returns:
            Lista de instâncias do modelo (pode estar vazia)

        Exemplo:
            # Primeiros 20 posts, mais recentes primeiro
            posts = await repo.get_multi(limit=20, order_by="created_at", desc=True)

            # Página 2 com 10 itens por página
            items = await repo.get_multi(skip=10, limit=10)
        """
        query = select(self.model)

        # Aplica ordenação se especificada
        if order_by:
            column = getattr(self.model, order_by)
            query = query.order_by(column.desc() if desc else column.asc())

        # Aplica paginação
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self) -> int:
        """
        Conta o total de registros na tabela.

        Útil para cálculo de páginas na paginação e estatísticas.

        Returns:
            Número total de registros

        Exemplo:
            total = await repo.count()
            total_pages = (total + per_page - 1) // per_page
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        """
        Cria um novo registro no banco de dados.

        Realiza commit automático após a inserção e refresh para
        carregar valores gerados pelo banco (UUID, timestamps, etc).

        Args:
            obj_in: Dicionário com dados para criação.
                    As chaves devem corresponder aos campos do modelo.

        Returns:
            Instância do modelo criada e persistida

        Raises:
            IntegrityError: Se violar constraint única ou FK

        Exemplo:
            user = await repo.create({
                "name": "João Silva",
                "email": "joao@example.com",
                "password_hash": hashed_password
            })
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)  # Carrega valores gerados pelo banco
        return db_obj

    async def update(
        self, db_obj: ModelType, obj_in: dict[str, Any]
    ) -> ModelType:
        """
        Atualiza um registro existente.

        Aplica todos os campos presentes no dicionário, incluindo valores None.
        Isso permite limpar campos opcionais quando necessario.

        Args:
            db_obj: Instância do modelo a ser atualizada
            obj_in: Dicionário com campos a atualizar.

        Returns:
            Instância atualizada e persistida

        Exemplo:
            user = await repo.get(user_id)
            updated_user = await repo.update(user, {"name": "Novo Nome"})
        """
        for field, value in obj_in.items():
            # Aplica todos os campos presentes no dicionario
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> bool:
        """
        Remove um registro por seu ID.

        Realiza soft-delete ou hard-delete dependendo da configuração do modelo.
        Este método faz hard-delete (remoção física).

        Args:
            id: UUID do registro a ser removido

        Returns:
            True se removido com sucesso, False se não encontrado

        Exemplo:
            if await repo.delete(user_id):
                print("Usuário removido")
            else:
                print("Usuário não encontrado")
        """
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """
        Verifica se um registro existe sem carregá-lo completamente.

        Mais eficiente que get() quando só precisamos saber se existe,
        pois usa COUNT ao invés de SELECT *.

        Args:
            id: UUID do registro a verificar

        Returns:
            True se existe, False caso contrário

        Exemplo:
            if not await repo.exists(category_id):
                raise HTTPException(404, "Categoria não encontrada")
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        return result.scalar_one() > 0
