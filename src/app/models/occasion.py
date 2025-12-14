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

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import JSONBType, TimestampMixin, UUIDMixin


class Occasion(Base, UUIDMixin, TimestampMixin):
    """
    Ocasiao para presentear.

    Atributos:
        id: UUID primary key
        name: Nome da ocasiao (ex: "Natal", "Aniversario")
        slug: Slug unico para URL
        description: Descricao curta da ocasiao (para listagens)
        content: Conteudo completo em Markdown (como posts)
        icon: Emoji ou icone da ocasiao
        image_url: URL da imagem de capa
        seo_title: Titulo para SEO (meta title)
        seo_description: Descricao para SEO (meta description)
        is_active: Se a ocasiao esta ativa
        display_order: Ordem de exibicao
        next_review_date: Data da proxima revisao (mes/ano)
        created_at: Data de criacao
        updated_at: Data de atualizacao
    """

    __tablename__ = "occasions"

    # Campos basicos
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Imagem e SEO
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    seo_focus_keyword: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seo_title: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)

    # Controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Proxima revisao (primeiro dia do mes para simplificar)
    next_review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Tags (array JSON - usa JSONBType para compatibilidade com SQLite em testes)
    tags: Mapped[list] = mapped_column(JSONBType, default=list, server_default="[]")

    # Custos de IA (para calcular ROI)
    ai_tokens_used: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
        comment="Total de tokens consumidos em geracoes de IA",
    )
    ai_prompt_tokens: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
        comment="Tokens de entrada (prompt) consumidos em geracoes de IA",
    )
    ai_completion_tokens: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
        comment="Tokens de saida (completion) consumidos em geracoes de IA",
    )
    ai_cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=6), default=Decimal("0"), server_default="0",
        comment="Custo total em USD das geracoes de IA",
    )
    ai_generations_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
        comment="Numero de vezes que IA foi usada para gerar conteudo",
    )

    # Indices
    __table_args__ = (
        Index("idx_occasions_slug", "slug"),
        Index("idx_occasions_active_order", "is_active", "display_order"),
        Index("idx_occasions_next_review", "next_review_date"),
        Index("idx_occasions_tags", "tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Occasion {self.name} ({self.slug})>"
