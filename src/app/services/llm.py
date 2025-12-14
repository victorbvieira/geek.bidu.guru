"""
Servico de LLM usando LiteLLM.

LiteLLM e um wrapper universal que suporta:
- OpenAI (GPT-4, GPT-4o, GPT-3.5)
- Anthropic (Claude 3)
- Google (Gemini)
- Groq, Together, etc.

Funcionalidades:
- Geracao de texto com system/user prompts
- Geracao de conteudo estruturado (JSON)
- Streaming de respostas
- Retry automatico com backoff
- Cache de respostas (opcional)
"""

import json
import logging
from typing import AsyncIterator, Literal

import litellm
from litellm import acompletion
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Configuracao do LiteLLM
# =============================================================================

# Configura chaves de API para cada provider
# LiteLLM detecta automaticamente qual provider usar pelo prefixo do modelo
if settings.openai_api_key:
    litellm.openai_key = settings.openai_api_key

if settings.anthropic_api_key:
    litellm.anthropic_key = settings.anthropic_api_key

if settings.gemini_api_key:
    # Gemini usa variavel de ambiente GEMINI_API_KEY
    # Modelos: gemini/gemini-pro, gemini/gemini-1.5-flash, gemini/gemini-1.5-pro
    import os
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

if settings.openrouter_api_key:
    # OpenRouter usa header especial, configurado via api_key no call
    # Modelos: openrouter/mistralai/mistral-7b-instruct, openrouter/meta-llama/llama-3-8b-instruct
    pass

# Desabilita telemetria
litellm.telemetry = False

# Habilita logging em desenvolvimento
if settings.is_development:
    litellm.set_verbose = True


# =============================================================================
# Mapeamento de Modelos por Provider
# =============================================================================

# Prefixos de modelo por provider (LiteLLM usa isso para rotear)
# OpenAI: gpt-4, gpt-4o, gpt-4o-mini, gpt-3.5-turbo
# Anthropic: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
# Gemini: gemini/gemini-pro, gemini/gemini-1.5-flash, gemini/gemini-1.5-pro
# OpenRouter: openrouter/<provider>/<model> (ex: openrouter/mistralai/mistral-7b-instruct)
# Groq: groq/llama-3.1-8b-instant, groq/mixtral-8x7b-32768

def get_model_for_task(task: Literal["content", "simple", "default"]) -> str:
    """
    Retorna o modelo apropriado para o tipo de tarefa.

    Args:
        task: Tipo de tarefa (content=posts/listicles, simple=slugs/tags, default=padrao)

    Returns:
        Nome do modelo no formato LiteLLM
    """
    if task == "content" and settings.llm_model_content:
        return settings.llm_model_content
    elif task == "simple" and settings.llm_model_simple:
        return settings.llm_model_simple
    return settings.llm_default_model


def get_api_key_for_model(model: str) -> str | None:
    """
    Retorna a API key apropriada para o modelo.

    Args:
        model: Nome do modelo no formato LiteLLM

    Returns:
        API key ou None se usar a configuracao global
    """
    if model.startswith("openrouter/"):
        return settings.openrouter_api_key
    # Outros providers usam a configuracao global do litellm
    return None


# =============================================================================
# Modelos de Resposta
# =============================================================================


class LLMResponse(BaseModel):
    """Resposta padronizada do LLM."""

    content: str
    model: str
    usage: dict[str, int] | None = None
    finish_reason: str | None = None


class GeneratedPost(BaseModel):
    """Post gerado pelo LLM."""

    title: str
    meta_description: str
    content: str  # HTML ou Markdown
    keywords: list[str]


class GeneratedProductDescription(BaseModel):
    """Descricao de produto gerada pelo LLM."""

    short_description: str
    long_description: str
    highlights: list[str]
    target_audience: str


# =============================================================================
# Servico Principal
# =============================================================================


class LLMService:
    """
    Servico para interacao com LLMs via LiteLLM.

    Uso:
        llm = LLMService()

        # Geracao simples
        response = await llm.generate("Escreva um texto sobre...")

        # Com system prompt
        response = await llm.generate(
            "Crie um titulo para...",
            system="Voce e um redator especializado em presentes geek."
        )

        # Resposta estruturada (JSON)
        post = await llm.generate_structured(
            prompt="Crie um post sobre Funko Pop",
            schema=GeneratedPost
        )
    """

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: int | None = None,
    ):
        """
        Inicializa o servico de LLM.

        Args:
            model: Modelo a usar (ex: gpt-4o-mini, claude-3-haiku-20240307)
            temperature: Criatividade (0.0 = determinista, 1.0 = criativo)
            max_tokens: Maximo de tokens na resposta
            timeout: Timeout em segundos
        """
        self.model = model or settings.llm_default_model
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.timeout = timeout or settings.llm_timeout

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """
        Gera texto a partir de um prompt.

        Args:
            prompt: Texto do usuario
            system: System prompt (instrucoes para o modelo)
            model: Override do modelo
            temperature: Override da temperatura
            max_tokens: Override de max_tokens

        Returns:
            LLMResponse com conteudo gerado

        Raises:
            LLMError: Se houver erro na geracao
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        try:
            # Determina modelo e API key
            use_model = model or self.model
            api_key = get_api_key_for_model(use_model)

            # Monta kwargs da chamada
            tokens_value = max_tokens or self.max_tokens
            is_gpt5 = "gpt-5" in use_model or "gpt-4.1" in use_model

            call_kwargs = {
                "model": use_model,
                "messages": messages,
                "timeout": self.timeout,
            }

            # GPT-5-nano so aceita temperature=1 (default), nao enviar o parametro
            # https://platform.openai.com/docs/models/gpt-5-nano
            if not is_gpt5:
                call_kwargs["temperature"] = temperature if temperature is not None else self.temperature

            # GPT-5 e modelos mais novos usam max_completion_tokens em vez de max_tokens
            if is_gpt5:
                call_kwargs["max_completion_tokens"] = tokens_value
            else:
                call_kwargs["max_tokens"] = tokens_value

            # Adiciona API key se necessario (ex: OpenRouter)
            if api_key:
                call_kwargs["api_key"] = api_key

            response = await acompletion(**call_kwargs)

            # Log para debug da resposta
            raw_content = response.choices[0].message.content
            logger.info(f"LLM Response - model: {response.model}, finish_reason: {response.choices[0].finish_reason}")
            logger.info(f"LLM Response - raw_content type: {type(raw_content)}, value: {repr(raw_content)[:200]}")

            # Trata caso de content None
            content = raw_content if raw_content is not None else ""

            return LLMResponse(
                content=content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                if response.usage
                else None,
                finish_reason=response.choices[0].finish_reason,
            )

        except Exception as e:
            logger.error(f"Erro ao gerar texto com LLM: {e}")
            raise LLMError(f"Falha na geracao de texto: {str(e)}") from e

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
    ) -> BaseModel:
        """
        Gera resposta estruturada (JSON) a partir de um prompt.

        O modelo e instruido a retornar JSON valido conforme o schema.

        Args:
            prompt: Texto do usuario
            schema: Pydantic model para validacao
            system: System prompt adicional
            model: Override do modelo
            temperature: Override da temperatura

        Returns:
            Instancia do schema preenchida

        Raises:
            LLMError: Se houver erro na geracao ou parsing
        """
        # Adiciona instrucoes de formato JSON ao system prompt
        schema_json = json.dumps(schema.model_json_schema(), indent=2, ensure_ascii=False)

        json_instructions = f"""Retorne APENAS um JSON valido, sem markdown ou texto adicional.
O JSON deve seguir exatamente este schema:

{schema_json}

Responda apenas com o JSON, sem ```json ou qualquer outro texto."""

        full_system = f"{system}\n\n{json_instructions}" if system else json_instructions

        response = await self.generate(
            prompt=prompt,
            system=full_system,
            model=model,
            temperature=temperature if temperature is not None else 0.3,  # Mais determinista para JSON
            max_tokens=self.max_tokens,
        )

        # Parse do JSON
        try:
            # Remove possiveis ```json que o modelo pode incluir
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]

            data = json.loads(content.strip())
            return schema.model_validate(data)

        except json.JSONDecodeError as e:
            logger.error(f"JSON invalido retornado pelo LLM: {response.content}")
            raise LLMError(f"LLM retornou JSON invalido: {str(e)}") from e

        except Exception as e:
            logger.error(f"Erro ao validar resposta do LLM: {e}")
            raise LLMError(f"Erro ao processar resposta: {str(e)}") from e

    async def generate_stream(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Gera texto em streaming (para respostas longas ou UI em tempo real).

        Args:
            prompt: Texto do usuario
            system: System prompt
            model: Override do modelo
            temperature: Override da temperatura
            max_tokens: Override de max_tokens

        Yields:
            Chunks de texto conforme sao gerados

        Example:
            async for chunk in llm.generate_stream("Escreva um artigo sobre..."):
                print(chunk, end="", flush=True)
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        try:
            # Determina modelo e API key
            use_model = model or self.model
            api_key = get_api_key_for_model(use_model)

            # Monta kwargs da chamada
            call_kwargs = {
                "model": use_model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
                "timeout": self.timeout,
                "stream": True,
            }

            # Adiciona API key se necessario (ex: OpenRouter)
            if api_key:
                call_kwargs["api_key"] = api_key

            response = await acompletion(**call_kwargs)

            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Erro no streaming do LLM: {e}")
            raise LLMError(f"Falha no streaming: {str(e)}") from e


# =============================================================================
# Excecao Personalizada
# =============================================================================


class LLMError(Exception):
    """Erro ao interagir com o LLM."""

    pass


# =============================================================================
# Instancia Global (singleton)
# =============================================================================


_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """
    Retorna instancia global do servico de LLM.

    Uso com dependency injection do FastAPI:

        @router.post("/generate")
        async def generate(llm: LLMService = Depends(get_llm_service)):
            response = await llm.generate("...")
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
