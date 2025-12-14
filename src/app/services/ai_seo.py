"""
Servico de geracao de SEO usando IA.

Este servico utiliza as configuracoes armazenadas no banco (AIConfig)
para gerar titulos, descricoes e keywords otimizadas para SEO.

Usa LiteLLM para compatibilidade com multiplos provedores.
"""

import logging
import re
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_config import AIConfig, AIProvider, AIUseCase
from app.repositories.ai_config import AIConfigRepository
from app.services.llm import LLMService, LLMError, get_api_key_for_model

logger = logging.getLogger(__name__)


# Precos por 1M tokens (em USD) - atualizado em Dez/2025
# https://openai.com/api/pricing/
MODEL_PRICING = {
    # OpenAI GPT-5 Family
    "gpt-5-nano": {"input": 0.05, "output": 0.40},
    "gpt-5-mini": {"input": 0.15, "output": 0.60},
    "gpt-5": {"input": 2.50, "output": 10.00},
    # OpenAI Legacy
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    # Gemini (via OpenRouter ou direto)
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    # Claude (via OpenRouter)
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
}


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> Decimal:
    """
    Calcula o custo em USD baseado no modelo e tokens usados.

    Args:
        model: Nome do modelo (ex: gpt-4o-mini)
        prompt_tokens: Tokens do prompt (input)
        completion_tokens: Tokens da resposta (output)

    Returns:
        Custo total em USD (Decimal com 6 casas)
    """
    # Normaliza nome do modelo (remove prefixos como openrouter/, gemini/)
    model_key = model.split("/")[-1].split(":")[0]

    # Busca preco do modelo ou usa um default conservador
    pricing = MODEL_PRICING.get(model_key, {"input": 1.00, "output": 3.00})

    # Calcula custo (precos sao por 1M tokens)
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]

    return Decimal(str(round(input_cost + output_cost, 6)))


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
        subtitle: str | None = None,
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
            subtitle: Subtitulo do conteudo (para posts)
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

        # NOVA ABORDAGEM: system_prompt = instrucoes, user_prompt = dados
        # Se o prompt tem placeholders, extraimos a parte de instrucoes para system
        # e montamos o user_prompt com os dados

        has_placeholders = "{{title}}" in config.system_prompt or "{{content}}" in config.system_prompt

        if has_placeholders:
            # Remove os placeholders do system_prompt (mantem apenas instrucoes)
            # O system_prompt original fica como instrucao geral
            system_prompt = config.system_prompt

            # Remove a secao de CONTEXTO DO POST do system_prompt
            # pois ela vai no user_prompt agora
            # Remove bloco de CONTEXTO ate a proxima secao (REGRAS, etc)
            system_prompt = re.sub(
                r'CONTEXTO DO POST:.*?(?=\n\n[A-Z]|\nREGRAS|\nRESPONDA|\Z)',
                '',
                system_prompt,
                flags=re.DOTALL | re.IGNORECASE
            ).strip()

            # Monta user_prompt com os dados do conteudo
            user_parts = []
            if title:
                user_parts.append(f"Titulo: {title}")
            if subtitle:
                user_parts.append(f"Subtitulo: {subtitle}")
            if content:
                # Limita conteudo para nao exceder tokens
                content_text = content[:2000] if len(content) > 2000 else content
                user_parts.append(f"Conteudo:\n{content_text}")
            if category:
                user_parts.append(f"Categoria: {category}")
            if keywords:
                user_parts.append(f"Keywords atuais: {', '.join(keywords)}")
            if product_name:
                user_parts.append(f"Produto: {product_name}")

            user_prompt = "\n\n".join(user_parts) if user_parts else "Gere o conteudo."
        else:
            # Prompt antigo sem placeholders - mantem comportamento original
            system_prompt = config.system_prompt
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
                system=system_prompt,
            )

            # Extrai informacoes de uso de tokens
            tokens_used = 0
            prompt_tokens = 0
            completion_tokens = 0
            cost_usd = Decimal("0")

            if response.usage:
                prompt_tokens = response.usage.get("prompt_tokens", 0)
                completion_tokens = response.usage.get("completion_tokens", 0)
                tokens_used = response.usage.get("total_tokens", 0)
                cost_usd = calculate_cost(response.model, prompt_tokens, completion_tokens)

            return {
                "generated_content": response.content.strip(),
                "model_used": response.model,
                "tokens_used": tokens_used,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": float(cost_usd),
                "use_case": use_case.value,
                "finish_reason": response.finish_reason,
                # Dados para logging (prefixo _ indica campo interno)
                "_system_prompt": system_prompt,
                "_user_prompt": user_prompt,
                "_provider": config.provider.value,
                "_temperature": config.temperature,
                "_max_tokens": config.max_tokens,
            }

        except LLMError as e:
            logger.error(f"Erro ao gerar SEO ({use_case.value}): {e}")
            raise

    def _replace_placeholders(
        self,
        template: str,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        content: str | None = None,
        keywords: list[str] | None = None,
        category: str | None = None,
        product_name: str | None = None,
    ) -> str:
        """
        Substitui placeholders no template por valores reais.

        Placeholders suportados:
        - {{title}}: Titulo do conteudo
        - {{subtitle}}: Subtitulo do conteudo
        - {{content}}: Conteudo completo (limitado a 2000 chars)
        - {{keywords}}: Palavras-chave separadas por virgula
        - {{category}}: Categoria
        - {{product_name}}: Nome do produto
        """
        result = template

        # Substitui cada placeholder
        result = result.replace("{{title}}", title or "(sem titulo)")
        result = result.replace("{{subtitle}}", subtitle or "(sem subtitulo)")

        # Limita conteudo para nao exceder tokens
        content_text = content[:2000] if content and len(content) > 2000 else (content or "(sem conteudo)")
        result = result.replace("{{content}}", content_text)

        result = result.replace("{{keywords}}", ", ".join(keywords) if keywords else "(sem keywords)")
        result = result.replace("{{category}}", category or "(sem categoria)")
        result = result.replace("{{product_name}}", product_name or "(sem produto)")

        return result

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
