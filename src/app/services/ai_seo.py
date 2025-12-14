"""
Servico de geracao de SEO usando IA.

Este servico utiliza as configuracoes armazenadas no banco (AIConfig)
para gerar titulos, descricoes e keywords otimizadas para SEO.

Usa LiteLLM para compatibilidade com multiplos provedores.
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_config import AIConfig, AIProvider, AIUseCase
from app.repositories.ai_config import AIConfigRepository
from app.services.llm import LLMService, LLMError, get_api_key_for_model

logger = logging.getLogger(__name__)


class AISEOService:
    """
    Servico para geracao de conteudo SEO usando IA.

    Busca a configuracao apropriada do banco e usa o modelo configurado
    para gerar o conteudo solicitado.
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa o servico com a sessao do banco.

        Args:
            db: Sessao assincrona do SQLAlchemy
        """
        self.db = db
        self.repo = AIConfigRepository(db)

    async def generate(
        self,
        use_case: AIUseCase,
        *,
        title: str | None = None,
        content: str | None = None,
        keywords: list[str] | None = None,
        category: str | None = None,
        product_name: str | None = None,
        target_audience: str | None = None,
    ) -> dict[str, Any]:
        """
        Gera conteudo SEO usando a configuracao do caso de uso.

        Args:
            use_case: Tipo de conteudo a gerar (seo_title, seo_description, etc.)
            title: Titulo original do conteudo
            content: Conteudo completo para analise
            keywords: Palavras-chave existentes
            category: Categoria do conteudo
            product_name: Nome do produto (se aplicavel)
            target_audience: Publico-alvo

        Returns:
            Dicionario com:
            - generated_content: Conteudo gerado
            - model_used: Modelo que gerou
            - tokens_used: Tokens consumidos (se disponivel)

        Raises:
            ValueError: Se a configuracao nao existe ou esta inativa
            LLMError: Se houver erro na geracao
        """
        # Busca configuracao ativa para o caso de uso
        config = await self.repo.get_active_by_use_case(use_case)
        if not config:
            raise ValueError(
                f"Nenhuma configuracao ativa encontrada para: {use_case.value}"
            )

        # Monta o prompt do usuario com o contexto fornecido
        user_prompt = self._build_user_prompt(
            use_case=use_case,
            title=title,
            content=content,
            keywords=keywords,
            category=category,
            product_name=product_name,
            target_audience=target_audience,
        )

        # Configura o servico LLM com os parametros da config
        llm = LLMService(
            model=config.full_model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        try:
            # Gera o conteudo
            response = await llm.generate(
                prompt=user_prompt,
                system=config.system_prompt,
            )

            return {
                "generated_content": response.content.strip(),
                "model_used": response.model,
                "tokens_used": response.usage.get("total_tokens") if response.usage else None,
                "use_case": use_case.value,
            }

        except LLMError as e:
            logger.error(f"Erro ao gerar SEO ({use_case.value}): {e}")
            raise

    def _build_user_prompt(
        self,
        use_case: AIUseCase,
        title: str | None,
        content: str | None,
        keywords: list[str] | None,
        category: str | None,
        product_name: str | None,
        target_audience: str | None,
    ) -> str:
        """
        Constroi o prompt do usuario baseado no caso de uso.

        Args:
            use_case: Tipo de conteudo
            title: Titulo original
            content: Conteudo completo
            keywords: Palavras-chave
            category: Categoria
            product_name: Nome do produto
            target_audience: Publico-alvo

        Returns:
            Prompt formatado para o modelo
        """
        parts = []

        # Adiciona contexto baseado no caso de uso
        if use_case == AIUseCase.SEO_TITLE:
            parts.append("Crie um titulo SEO otimizado para o seguinte conteudo:")
        elif use_case == AIUseCase.SEO_DESCRIPTION:
            parts.append("Crie uma meta description SEO para o seguinte conteudo:")
        elif use_case == AIUseCase.SEO_KEYWORDS:
            parts.append("Sugira palavras-chave SEO para o seguinte conteudo:")
        elif use_case == AIUseCase.PRODUCT_DESCRIPTION:
            parts.append("Crie uma descricao de produto para:")
        else:
            parts.append("Gere conteudo para:")

        # Adiciona o titulo se fornecido
        if title:
            parts.append(f"\nTitulo: {title}")

        # Adiciona o conteudo se fornecido
        if content:
            # Limita o conteudo para nao exceder tokens
            max_content = content[:2000] if len(content) > 2000 else content
            parts.append(f"\nConteudo:\n{max_content}")

        # Adiciona metadata adicional
        if product_name:
            parts.append(f"\nProduto: {product_name}")

        if category:
            parts.append(f"\nCategoria: {category}")

        if keywords:
            parts.append(f"\nPalavras-chave atuais: {', '.join(keywords)}")

        if target_audience:
            parts.append(f"\nPublico-alvo: {target_audience}")

        return "\n".join(parts)

    async def generate_seo_title(
        self,
        title: str,
        content: str | None = None,
        category: str | None = None,
    ) -> str:
        """
        Gera titulo SEO otimizado.

        Args:
            title: Titulo original
            content: Conteudo para contexto
            category: Categoria do conteudo

        Returns:
            Titulo SEO gerado (max 60 caracteres)
        """
        result = await self.generate(
            AIUseCase.SEO_TITLE,
            title=title,
            content=content,
            category=category,
        )
        return result["generated_content"]

    async def generate_seo_description(
        self,
        title: str,
        content: str | None = None,
        category: str | None = None,
    ) -> str:
        """
        Gera meta description SEO.

        Args:
            title: Titulo do conteudo
            content: Conteudo para contexto
            category: Categoria

        Returns:
            Meta description gerada (120-160 caracteres)
        """
        result = await self.generate(
            AIUseCase.SEO_DESCRIPTION,
            title=title,
            content=content,
            category=category,
        )
        return result["generated_content"]

    async def generate_seo_keywords(
        self,
        title: str,
        content: str | None = None,
        category: str | None = None,
    ) -> list[str]:
        """
        Gera sugestoes de palavras-chave SEO.

        Args:
            title: Titulo do conteudo
            content: Conteudo para contexto
            category: Categoria

        Returns:
            Lista de palavras-chave sugeridas
        """
        result = await self.generate(
            AIUseCase.SEO_KEYWORDS,
            title=title,
            content=content,
            category=category,
        )
        # Separa as keywords (podem vir separadas por virgula ou quebra de linha)
        keywords_str = result["generated_content"]
        keywords = [
            k.strip()
            for k in keywords_str.replace("\n", ",").split(",")
            if k.strip()
        ]
        return keywords

    async def generate_product_description(
        self,
        product_name: str,
        category: str | None = None,
        price: float | None = None,
        platform: str | None = None,
        raw_info: str | None = None,
    ) -> dict[str, str]:
        """
        Gera descricoes de produto (curta e longa).

        Args:
            product_name: Nome do produto
            category: Categoria
            price: Preco
            platform: Plataforma (Amazon, ML, Shopee)
            raw_info: Informacoes brutas do produto

        Returns:
            Dicionario com short_description e long_description
        """
        # Monta contexto
        content_parts = [f"Produto: {product_name}"]
        if category:
            content_parts.append(f"Categoria: {category}")
        if price:
            content_parts.append(f"Preco: R$ {price:.2f}")
        if platform:
            content_parts.append(f"Plataforma: {platform}")
        if raw_info:
            content_parts.append(f"Informacoes: {raw_info}")

        result = await self.generate(
            AIUseCase.PRODUCT_DESCRIPTION,
            product_name=product_name,
            content="\n".join(content_parts),
            category=category,
        )

        # O modelo deve retornar descricao curta e longa separadas
        # Tenta separar se vier em formato estruturado
        generated = result["generated_content"]

        # Se vier tudo junto, divide em short e long
        if "CURTA:" in generated.upper() and "LONGA:" in generated.upper():
            parts = generated.split("LONGA:", 1)
            short = parts[0].replace("CURTA:", "").strip()
            long_desc = parts[1].strip() if len(parts) > 1 else short
        else:
            # Se nao vier estruturado, usa o primeiro paragrafo como curto
            paragraphs = [p.strip() for p in generated.split("\n\n") if p.strip()]
            short = paragraphs[0][:150] if paragraphs else generated[:150]
            long_desc = generated

        return {
            "short_description": short,
            "long_description": long_desc,
            "model_used": result["model_used"],
        }


# Funcao factory para dependency injection
def get_ai_seo_service(db: AsyncSession) -> AISEOService:
    """
    Factory para o servico de SEO com IA.

    Uso com FastAPI:
        @router.post("/generate-seo")
        async def generate_seo(
            db: DBSession,
            ai_seo: AISEOService = Depends(get_ai_seo_service)
        ):
            ...
    """
    return AISEOService(db)
