"""
Repositorio base com operacoes CRUD genericas.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repositorio base com operacoes CRUD."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> ModelType | None:
        """Busca por ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_field(self, field: str, value: Any) -> ModelType | None:
        """Busca por campo especifico."""
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
        """Lista com paginacao."""
        query = select(self.model)

        if order_by:
            column = getattr(self.model, order_by)
            query = query.order_by(column.desc() if desc else column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Conta total de registros."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        """Cria novo registro."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, db_obj: ModelType, obj_in: dict[str, Any]
    ) -> ModelType:
        """Atualiza registro existente."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> bool:
        """Remove registro por ID."""
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """Verifica se registro existe."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        return result.scalar_one() > 0
