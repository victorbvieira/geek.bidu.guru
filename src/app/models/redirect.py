"""
Modelo de Redirect para URLs antigas.

Armazena redirecionamentos 301 permanentes para migracao de URLs.
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Redirect(Base, UUIDMixin, TimestampMixin):
    """
    Modelo para armazenar redirects 301.

    Attributes:
        old_path: URL antiga (sem dominio, ex: "artigo/meu-post")
        new_path: URL nova (com barra inicial, ex: "/blog/meu-post")
        is_pattern: Se True, old_path e um prefixo para match parcial
        is_active: Se o redirect esta ativo
        hit_count: Contador de quantas vezes o redirect foi usado
    """

    __tablename__ = "redirects"

    old_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        index=True,
        comment="URL antiga (sem dominio)",
    )
    new_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="URL nova (com / inicial)",
    )
    is_pattern: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Se True, old_path e prefixo para match parcial",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        comment="Se o redirect esta ativo",
    )
    hit_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Contador de uso do redirect",
    )

    def __repr__(self) -> str:
        return f"<Redirect {self.old_path} -> {self.new_path}>"
