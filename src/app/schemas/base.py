"""
Base schemas e configuracoes comuns para Pydantic.

Padrao seguido:
- SchemaBase: campos compartilhados
- SchemaCreate: campos para criacao (herda de Base)
- SchemaUpdate: campos opcionais para atualizacao
- Schema: resposta completa com campos do banco (id, timestamps)
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Schema base com configuracoes padrao."""

    model_config = ConfigDict(
        from_attributes=True,  # Permite criar schema a partir de ORM model
        str_strip_whitespace=True,  # Remove espacos em branco
        populate_by_name=True,  # Permite usar alias ou nome do campo
    )


class TimestampSchema(BaseSchema):
    """Schema com timestamps padrao."""

    created_at: datetime
    updated_at: datetime


class IDSchema(BaseSchema):
    """Schema com ID UUID."""

    id: UUID


class ResponseSchema(IDSchema, TimestampSchema):
    """Schema base para respostas completas (id + timestamps)."""

    pass


# -----------------------------------------------------------------------------
# Schemas de Paginacao
# -----------------------------------------------------------------------------


class PaginationParams(BaseModel):
    """Parametros de paginacao."""

    page: int = Field(default=1, ge=1, description="Numero da pagina")
    per_page: int = Field(default=20, ge=1, le=100, description="Itens por pagina")

    @property
    def offset(self) -> int:
        """Calcula o offset para a query."""
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseSchema):
    """Resposta paginada generica."""

    items: list[Any]
    total: int
    page: int
    per_page: int
    pages: int

    @classmethod
    def create(
        cls, items: list[Any], total: int, page: int, per_page: int
    ) -> "PaginatedResponse":
        """Cria resposta paginada."""
        pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        )


# -----------------------------------------------------------------------------
# Schemas de Mensagens/Status
# -----------------------------------------------------------------------------


class MessageResponse(BaseSchema):
    """Resposta simples com mensagem."""

    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    """Resposta de erro."""

    detail: str
    error_code: str | None = None
