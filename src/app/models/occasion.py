"""
Modelo de Ocasiao.

Ocasioes representam momentos especiais para presentear:
- Natal
- Aniversario
- Dia dos Namorados
- Dia das Maes/Pais
- Formatura
- etc.

Produtos e posts podem ser associados a multiplas ocasioes.
"""

from typing import Optional

from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Occasion(Base, UUIDMixin, TimestampMixin):
    """
    Ocasiao para presentear.

    Atributos:
        id: UUID primary key
        name: Nome da ocasiao (ex: "Natal", "Aniversario")
        slug: Slug unico para URL
        description: Descricao da ocasiao
        icon: Emoji ou icone da ocasiao
        image_url: URL da imagem de capa
        seo_title: Titulo para SEO (meta title)
        seo_description: Descricao para SEO (meta description)
        is_active: Se a ocasiao esta ativa
        display_order: Ordem de exibicao
        created_at: Data de criacao
        updated_at: Data de atualizacao
    """

    __tablename__ = "occasions"

    # Campos basicos
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Imagem e SEO
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    seo_title: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)

    # Controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Indices
    __table_args__ = (
        Index("idx_occasions_slug", "slug"),
        Index("idx_occasions_active_order", "is_active", "display_order"),
    )

    def __repr__(self) -> str:
        return f"<Occasion {self.name} ({self.slug})>"
