"""
Mixins base para modelos SQLAlchemy.

Este módulo implementa o padrão Mixin para adicionar campos comuns
a todos os modelos do sistema, seguindo os princípios DRY (Don't Repeat Yourself)
e composição sobre herança.

Mixins disponíveis:
    - UUIDMixin: Adiciona campo UUID como chave primária
    - TimestampMixin: Adiciona campos de auditoria (created_at, updated_at)

Exemplo de uso:
    class MinhaEntidade(Base, UUIDMixin, TimestampMixin):
        __tablename__ = "minha_tabela"
        nome: Mapped[str] = mapped_column(String(100))

Notas:
    - Os mixins utilizam tanto `default` (Python) quanto `server_default` (PostgreSQL)
      para garantir que os valores sejam definidos em ambos os contextos
    - O campo UUID utiliza a função nativa do PostgreSQL `gen_random_uuid()`
      para melhor performance em operações de bulk insert
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """
    Mixin que adiciona campo UUID como chave primária.

    Utiliza UUID v4 para garantir unicidade global sem necessidade
    de coordenação centralizada. Isso facilita:
    - Geração de IDs no cliente antes de persistir
    - Integração entre sistemas distribuídos
    - Merge de dados de diferentes fontes

    Atributos:
        id (uuid.UUID): Identificador único universal da entidade.
            Gerado automaticamente pelo Python (default) ou pelo
            PostgreSQL (server_default) dependendo do contexto.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  # Gera UUID em Python (para testes e instâncias em memória)
        server_default=func.gen_random_uuid(),  # Gera UUID no PostgreSQL (para INSERTs diretos)
    )


class TimestampMixin:
    """
    Mixin que adiciona campos de auditoria temporal.

    Implementa campos para rastreamento de criação e atualização
    de registros, essencial para:
    - Auditoria e compliance
    - Ordenação cronológica
    - Cache invalidation
    - Debug e troubleshooting

    Atributos:
        created_at (datetime): Data/hora de criação do registro.
            Definido automaticamente na primeira inserção.
            Nunca deve ser alterado após criação.

        updated_at (datetime): Data/hora da última atualização.
            Atualizado automaticamente em cada UPDATE via
            `onupdate=datetime.utcnow`.

    Notas:
        - Utiliza timezone-aware datetime para compatibilidade
          com diferentes fusos horários
        - O valor é armazenado em UTC para consistência
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # Timestamp do servidor PostgreSQL
        default=datetime.utcnow,  # Timestamp do Python (para testes)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # Valor inicial igual a created_at
        default=datetime.utcnow,
        onupdate=datetime.utcnow,  # Atualiza automaticamente em cada UPDATE
    )
