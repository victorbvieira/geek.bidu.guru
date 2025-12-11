"""
Modelo de Usuario (Admin/Editor/Author).

Usuarios que podem criar e gerenciar conteudo no sistema.
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.post import Post


class UserRole(str, enum.Enum):
    """Roles disponiveis para usuarios."""

    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    AUTOMATION = "automation"  # Usuario especial para n8n/automacoes


class User(Base, UUIDMixin, TimestampMixin):
    """
    Usuario do sistema (admin, editor, autor).

    Atributos:
        id: UUID primary key
        name: Nome completo
        email: Email unico
        password_hash: Hash da senha (bcrypt)
        role: Papel do usuario (admin, editor, author, automation)
        is_active: Se o usuario esta ativo
        created_at: Data de criacao
        updated_at: Data de atualizacao
    """

    __tablename__ = "users"

    # Campos
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.AUTHOR,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relacionamentos
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author",
        lazy="selectin",
    )

    # Indices
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
        Index("idx_users_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"
