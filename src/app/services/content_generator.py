"""
Servico de Geracao de Conteudo com IA.

Usa LLM para gerar:
- Posts de produto
- Listicles
- Guias
- Posts de ofertas
- Descricoes de produto
"""

import logging
from typing import Any

from pydantic import BaseModel

from app.services.llm import (
    GeneratedPost,
    GeneratedProductDescription,
    LLMError,
    LLMService,
    get_llm_service,
)
from app.services.prompts import (
    COMPREHENSIVE_GUIDE,
    DEAL_POST,
    LISTICLE_TOP10,
    PRODUCT_DESCRIPTION,
    SINGLE_PRODUCT_POST,
    Persona,
    build_prompt,
    format_products_list,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Modelos de Entrada
# =============================================================================


class ProductInput(BaseModel):
    """Dados de produto para geracao de conteudo."""

    name: str
    price: float | None = None
    platform: str = "amazon"
    description: str | None = None
    rating: float | None = None
    category: str | None = None
    slug: str | None = None


class DealInput(BaseModel):
    """Dados de oferta para geracao de post."""

    product_name: str
    previous_price: float
    current_price: float
    platform: str = "amazon"


# =============================================================================
# Servico de Geracao
# =============================================================================


class ContentGenerator:
    """
    Servico para geracao de conteudo com IA.

    Uso:
        generator = ContentGenerator()

        # Gerar post de produto
        post = await generator.generate_product_post(
            product=ProductInput(name="Funko Pop", price=149.90, ...),
            keyword="funko pop star wars"
        )

        # Gerar listicle
        post = await generator.generate_listicle(
            theme="Presentes para Gamers",
            products=[...],
            keywords=["presentes gamer", "gifts gamer"]
        )
    """

    def __init__(self, llm: LLMService | None = None):
        """
        Inicializa o gerador de conteudo.

        Args:
            llm: Instancia do servico de LLM (usa padrao se None)
        """
        self.llm = llm or get_llm_service()

    async def generate_product_post(
        self,
        product: ProductInput,
        keyword: str,
        persona: Persona = Persona.PADRAO,
    ) -> GeneratedPost:
        """
        Gera post focado em um unico produto.

        Args:
            product: Dados do produto
            keyword: Palavra-chave SEO principal
            persona: Persona para ajuste de tom

        Returns:
            GeneratedPost com titulo, meta_description, content e keywords

        Raises:
            LLMError: Se houver erro na geracao
        """
        system, user = build_prompt(
            SINGLE_PRODUCT_POST,
            persona=persona,
            product_name=product.name,
            price=product.price or "N/A",
            platform=product.platform,
            description=product.description or "Produto geek de alta qualidade",
            rating=product.rating or "4.5",
            category=product.category or "Geek",
            keyword=keyword,
        )

        logger.info(f"Gerando post para produto: {product.name}")

        return await self.llm.generate_structured(
            prompt=user,
            system=system,
            schema=GeneratedPost,
            temperature=SINGLE_PRODUCT_POST.temperature,
        )

    async def generate_listicle(
        self,
        theme: str,
        products: list[ProductInput],
        keywords: list[str],
        occasion_or_persona: str = "fas de cultura geek",
        persona: Persona = Persona.PADRAO,
    ) -> GeneratedPost:
        """
        Gera listicle (Top 10) de produtos.

        Args:
            theme: Tema do listicle (ex: "Presentes para Gamers")
            products: Lista de produtos (minimo 5, ideal 10)
            keywords: Palavras-chave SEO
            occasion_or_persona: Para quem e a lista
            persona: Persona para ajuste de tom

        Returns:
            GeneratedPost com conteudo do listicle

        Raises:
            LLMError: Se houver erro na geracao
        """
        products_dicts = [p.model_dump() for p in products]
        products_list = format_products_list(products_dicts)

        system, user = build_prompt(
            LISTICLE_TOP10,
            persona=persona,
            theme=theme,
            products_list=products_list,
            occasion_or_persona=occasion_or_persona,
            keywords=", ".join(keywords),
        )

        logger.info(f"Gerando listicle: {theme} ({len(products)} produtos)")

        return await self.llm.generate_structured(
            prompt=user,
            system=system,
            schema=GeneratedPost,
            temperature=LISTICLE_TOP10.temperature,
        )

    async def generate_guide(
        self,
        topic: str,
        context: str,
        products: list[ProductInput],
        keywords: list[str],
        persona: Persona = Persona.PADRAO,
    ) -> GeneratedPost:
        """
        Gera guia completo sobre um tema.

        Args:
            topic: Topico do guia (ex: "Escolher o Melhor Funko Pop")
            context: Contexto adicional para o guia
            products: Produtos relacionados para mencionar
            keywords: Palavras-chave SEO
            persona: Persona para ajuste de tom

        Returns:
            GeneratedPost com conteudo do guia

        Raises:
            LLMError: Se houver erro na geracao
        """
        products_dicts = [p.model_dump() for p in products]
        products_list = format_products_list(products_dicts)

        system, user = build_prompt(
            COMPREHENSIVE_GUIDE,
            persona=persona,
            topic=topic,
            context=context,
            products_list=products_list,
            keywords=", ".join(keywords),
        )

        logger.info(f"Gerando guia: {topic}")

        return await self.llm.generate_structured(
            prompt=user,
            system=system,
            schema=GeneratedPost,
            temperature=COMPREHENSIVE_GUIDE.temperature,
        )

    async def generate_deal_post(
        self,
        deal: DealInput,
        persona: Persona = Persona.PADRAO,
    ) -> GeneratedPost:
        """
        Gera post de oferta/deal.

        Args:
            deal: Dados da oferta
            persona: Persona para ajuste de tom

        Returns:
            GeneratedPost com conteudo da oferta

        Raises:
            LLMError: Se houver erro na geracao
        """
        discount_percent = round(
            ((deal.previous_price - deal.current_price) / deal.previous_price) * 100
        )
        savings = deal.previous_price - deal.current_price

        system, user = build_prompt(
            DEAL_POST,
            persona=persona,
            product_name=deal.product_name,
            previous_price=f"{deal.previous_price:.2f}",
            current_price=f"{deal.current_price:.2f}",
            discount_percent=discount_percent,
            savings=f"{savings:.2f}",
            platform=deal.platform,
        )

        logger.info(f"Gerando post de deal: {deal.product_name} ({discount_percent}% off)")

        return await self.llm.generate_structured(
            prompt=user,
            system=system,
            schema=GeneratedPost,
            temperature=DEAL_POST.temperature,
        )

    async def generate_product_description(
        self,
        product: ProductInput,
        raw_info: str | None = None,
    ) -> GeneratedProductDescription:
        """
        Gera descricoes para um produto.

        Args:
            product: Dados do produto
            raw_info: Informacoes brutas adicionais (scraping, API, etc)

        Returns:
            GeneratedProductDescription com descricoes curta, longa, highlights

        Raises:
            LLMError: Se houver erro na geracao
        """
        system, user = build_prompt(
            PRODUCT_DESCRIPTION,
            product_name=product.name,
            category=product.category or "Geek",
            price=product.price or "N/A",
            platform=product.platform,
            raw_info=raw_info or product.description or "Produto geek",
        )

        logger.info(f"Gerando descricao para: {product.name}")

        return await self.llm.generate_structured(
            prompt=user,
            system=system,
            schema=GeneratedProductDescription,
            temperature=PRODUCT_DESCRIPTION.temperature,
        )


# =============================================================================
# Instancia Global
# =============================================================================


_content_generator: ContentGenerator | None = None


def get_content_generator() -> ContentGenerator:
    """Retorna instancia global do gerador de conteudo."""
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGenerator()
    return _content_generator
