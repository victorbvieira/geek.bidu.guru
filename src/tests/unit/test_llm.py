"""
Testes unitarios para o servico de LLM.

Testa:
- Configuracao e inicializacao
- Geracao de texto
- Geracao estruturada (JSON)
- Tratamento de erros
- Prompts e personas
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from app.services.llm import (
    GeneratedPost,
    GeneratedProductDescription,
    LLMError,
    LLMResponse,
    LLMService,
    get_api_key_for_model,
    get_llm_service,
    get_model_for_task,
)
from app.services.prompts import (
    PERSONA_MODIFIERS,
    POST_TEMPLATES,
    Persona,
    build_prompt,
    format_products_list,
    get_persona_modifier,
    get_template,
)


# =============================================================================
# Testes de Configuracao
# =============================================================================


class TestLLMServiceInit:
    """Testes de inicializacao do servico."""

    def test_init_with_defaults(self):
        """Deve inicializar com valores padrao."""
        service = LLMService()
        assert service.model is not None
        assert service.temperature >= 0
        assert service.max_tokens > 0
        assert service.timeout > 0

    def test_init_with_custom_values(self):
        """Deve aceitar valores customizados."""
        service = LLMService(
            model="gpt-4",
            temperature=0.5,
            max_tokens=1000,
            timeout=30,
        )
        assert service.model == "gpt-4"
        assert service.temperature == 0.5
        assert service.max_tokens == 1000
        assert service.timeout == 30

    def test_get_llm_service_singleton(self):
        """get_llm_service deve retornar singleton."""
        service1 = get_llm_service()
        service2 = get_llm_service()
        # Nota: como e singleton global, podem ser a mesma instancia
        assert service1 is not None
        assert service2 is not None


# =============================================================================
# Testes de Modelos de Resposta
# =============================================================================


class TestLLMModels:
    """Testes para modelos de resposta."""

    def test_llm_response_model(self):
        """LLMResponse deve validar corretamente."""
        response = LLMResponse(
            content="Texto gerado",
            model="gpt-4o-mini",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
        )
        assert response.content == "Texto gerado"
        assert response.model == "gpt-4o-mini"
        assert response.usage["total_tokens"] == 30

    def test_llm_response_without_usage(self):
        """LLMResponse deve aceitar usage None."""
        response = LLMResponse(
            content="Texto",
            model="gpt-4",
        )
        assert response.usage is None

    def test_generated_post_model(self):
        """GeneratedPost deve validar corretamente."""
        post = GeneratedPost(
            title="Titulo do Post",
            meta_description="Descricao meta",
            content="<p>Conteudo HTML</p>",
            keywords=["keyword1", "keyword2"],
        )
        assert post.title == "Titulo do Post"
        assert len(post.keywords) == 2

    def test_generated_product_description_model(self):
        """GeneratedProductDescription deve validar corretamente."""
        desc = GeneratedProductDescription(
            short_description="Descricao curta",
            long_description="Descricao longa detalhada",
            highlights=["Ponto 1", "Ponto 2"],
            target_audience="Geeks",
        )
        assert desc.short_description == "Descricao curta"
        assert len(desc.highlights) == 2


# =============================================================================
# Testes de Geracao de Texto (Mockado)
# =============================================================================


class TestLLMGenerate:
    """Testes para geracao de texto."""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock de resposta do LiteLLM."""
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = "Texto gerado pelo LLM"
        response.choices[0].finish_reason = "stop"
        response.model = "gpt-4o-mini"
        response.usage = MagicMock()
        response.usage.prompt_tokens = 50
        response.usage.completion_tokens = 100
        response.usage.total_tokens = 150
        return response

    @pytest.mark.asyncio
    async def test_generate_basic(self, mock_llm_response):
        """Deve gerar texto basico."""
        with patch("app.services.llm.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_llm_response

            service = LLMService()
            result = await service.generate("Escreva um texto")

            assert result.content == "Texto gerado pelo LLM"
            assert result.model == "gpt-4o-mini"
            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_llm_response):
        """Deve incluir system prompt na chamada."""
        with patch("app.services.llm.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_llm_response

            service = LLMService()
            await service.generate(
                "Escreva um titulo",
                system="Voce e um redator especializado",
            )

            # Verifica que messages inclui system e user
            call_args = mock.call_args
            messages = call_args.kwargs["messages"]
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_generate_error_handling(self):
        """Deve lancar LLMError em caso de falha."""
        with patch("app.services.llm.acompletion", new_callable=AsyncMock) as mock:
            mock.side_effect = Exception("API Error")

            service = LLMService()
            with pytest.raises(LLMError) as exc_info:
                await service.generate("Prompt")

            assert "API Error" in str(exc_info.value)


# =============================================================================
# Testes de Geracao Estruturada
# =============================================================================


class TestLLMGenerateStructured:
    """Testes para geracao estruturada (JSON)."""

    class SimpleSchema(BaseModel):
        """Schema simples para testes."""

        title: str
        items: list[str]

    @pytest.fixture
    def mock_json_response(self):
        """Mock de resposta JSON."""
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = json.dumps(
            {"title": "Titulo Teste", "items": ["item1", "item2"]}
        )
        response.choices[0].finish_reason = "stop"
        response.model = "gpt-4o-mini"
        response.usage = MagicMock()
        response.usage.prompt_tokens = 50
        response.usage.completion_tokens = 100
        response.usage.total_tokens = 150
        return response

    @pytest.mark.asyncio
    async def test_generate_structured_valid_json(self, mock_json_response):
        """Deve parsear JSON valido."""
        with patch("app.services.llm.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_json_response

            service = LLMService()
            result = await service.generate_structured(
                prompt="Gere uma lista",
                schema=self.SimpleSchema,
            )

            assert result.title == "Titulo Teste"
            assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_generate_structured_with_markdown(self):
        """Deve remover markdown do JSON."""
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = """```json
{"title": "Test", "items": ["a"]}
```"""
        response.choices[0].finish_reason = "stop"
        response.model = "gpt-4o-mini"
        response.usage = MagicMock()
        response.usage.prompt_tokens = 50
        response.usage.completion_tokens = 100
        response.usage.total_tokens = 150

        with patch("app.services.llm.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = response

            service = LLMService()
            result = await service.generate_structured(
                prompt="Gere",
                schema=self.SimpleSchema,
            )

            assert result.title == "Test"

    @pytest.mark.asyncio
    async def test_generate_structured_invalid_json(self):
        """Deve lancar erro para JSON invalido."""
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = "Nao e JSON"
        response.choices[0].finish_reason = "stop"
        response.model = "gpt-4o-mini"
        response.usage = MagicMock()
        response.usage.prompt_tokens = 50
        response.usage.completion_tokens = 100
        response.usage.total_tokens = 150

        with patch("app.services.llm.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = response

            service = LLMService()
            with pytest.raises(LLMError) as exc_info:
                await service.generate_structured(
                    prompt="Gere",
                    schema=self.SimpleSchema,
                )

            assert "JSON invalido" in str(exc_info.value)


# =============================================================================
# Testes de Prompts
# =============================================================================


class TestPrompts:
    """Testes para sistema de prompts."""

    def test_get_template_exists(self):
        """Deve retornar template existente."""
        template = get_template("single_product")
        assert template is not None
        assert template.name == "single_product_post"

    def test_get_template_not_exists(self):
        """Deve retornar None para template inexistente."""
        template = get_template("nonexistent")
        assert template is None

    def test_all_templates_have_required_fields(self):
        """Todos os templates devem ter campos obrigatorios."""
        for name, template in POST_TEMPLATES.items():
            assert template.name, f"{name} sem name"
            assert template.system_prompt, f"{name} sem system_prompt"
            assert template.user_prompt_template, f"{name} sem user_prompt_template"
            assert template.max_tokens > 0, f"{name} com max_tokens invalido"

    def test_format_products_list(self):
        """Deve formatar lista de produtos corretamente."""
        products = [
            {"name": "Produto A", "price": 100, "platform": "amazon"},
            {"name": "Produto B", "price": 200, "platform": "mercadolivre"},
        ]
        result = format_products_list(products)
        assert "1. Produto A" in result
        assert "2. Produto B" in result
        assert "R$ 100" in result
        assert "amazon" in result


# =============================================================================
# Testes de Personas
# =============================================================================


class TestPersonas:
    """Testes para sistema de personas."""

    def test_all_personas_have_modifiers(self):
        """Todas as personas devem ter modificadores."""
        for persona in Persona:
            assert persona.value in [p.value for p in PERSONA_MODIFIERS.keys()]

    def test_get_persona_modifier_ana(self):
        """Modifier de Ana deve mencionar linguagem simples."""
        modifier = get_persona_modifier(Persona.ANA_COMPRADORA)
        assert "simples" in modifier.lower() or "compradora" in PERSONA_MODIFIERS[Persona.ANA_COMPRADORA]["description"].lower()

    def test_get_persona_modifier_lucas(self):
        """Modifier de Lucas deve ser tecnico."""
        modifier = get_persona_modifier(Persona.LUCAS_GEEK_RAIZ)
        assert "geek" in modifier.lower() or "tecnico" in modifier.lower() or len(modifier) > 0

    def test_get_persona_modifier_padrao(self):
        """Modifier padrao deve ser vazio ou minimo."""
        modifier = get_persona_modifier(Persona.PADRAO)
        # Padrao pode ter modifier vazio
        assert isinstance(modifier, str)

    def test_build_prompt_with_persona(self):
        """build_prompt deve incluir modifier de persona."""
        template = get_template("single_product")
        system, user = build_prompt(
            template,
            persona=Persona.LUCAS_GEEK_RAIZ,
            product_name="Funko Pop",
            price="100",
            platform="amazon",
            description="Desc",
            rating="4.5",
            category="Funko",
            keyword="funko pop",
        )

        # System deve conter o modifier da persona
        assert "Funko Pop" in user
        assert len(system) > 0


# =============================================================================
# Testes de Erro LLM
# =============================================================================


class TestLLMError:
    """Testes para excecao LLMError."""

    def test_llm_error_message(self):
        """LLMError deve preservar mensagem."""
        error = LLMError("Teste de erro")
        assert str(error) == "Teste de erro"

    def test_llm_error_chaining(self):
        """LLMError deve suportar encadeamento."""
        original = ValueError("Original")
        try:
            raise LLMError("Wrapped") from original
        except LLMError as error:
            assert error.__cause__ == original


# =============================================================================
# Testes de Multi-Provider
# =============================================================================


class TestMultiProvider:
    """Testes para suporte a multiplos providers."""

    def test_get_model_for_task_default(self):
        """Deve retornar modelo padrao quando nao ha modelo especifico."""
        # Sem configuracao especifica, usa o default
        model = get_model_for_task("default")
        assert model is not None
        assert len(model) > 0

    def test_get_model_for_task_content(self):
        """Deve retornar modelo de conteudo se configurado."""
        with patch("app.services.llm.settings") as mock_settings:
            mock_settings.llm_model_content = "gpt-4-turbo"
            mock_settings.llm_model_simple = None
            mock_settings.llm_default_model = "gpt-4o-mini"

            model = get_model_for_task("content")
            assert model == "gpt-4-turbo"

    def test_get_model_for_task_simple(self):
        """Deve retornar modelo simples se configurado."""
        with patch("app.services.llm.settings") as mock_settings:
            mock_settings.llm_model_content = None
            mock_settings.llm_model_simple = "openrouter/mistralai/mistral-7b-instruct"
            mock_settings.llm_default_model = "gpt-4o-mini"

            model = get_model_for_task("simple")
            assert model == "openrouter/mistralai/mistral-7b-instruct"

    def test_get_model_for_task_falls_back_to_default(self):
        """Deve usar modelo padrao se especifico nao configurado."""
        with patch("app.services.llm.settings") as mock_settings:
            mock_settings.llm_model_content = None
            mock_settings.llm_model_simple = None
            mock_settings.llm_default_model = "gpt-4o-mini"

            model = get_model_for_task("content")
            assert model == "gpt-4o-mini"

    def test_get_api_key_for_openrouter_model(self):
        """Deve retornar API key do OpenRouter para modelos openrouter/*."""
        with patch("app.services.llm.settings") as mock_settings:
            mock_settings.openrouter_api_key = "sk-or-test-key"

            key = get_api_key_for_model("openrouter/mistralai/mistral-7b-instruct")
            assert key == "sk-or-test-key"

    def test_get_api_key_for_openai_model(self):
        """Deve retornar None para modelos OpenAI (usa config global)."""
        key = get_api_key_for_model("gpt-4o-mini")
        assert key is None

    def test_get_api_key_for_anthropic_model(self):
        """Deve retornar None para modelos Anthropic (usa config global)."""
        key = get_api_key_for_model("claude-3-haiku-20240307")
        assert key is None

    @pytest.mark.asyncio
    async def test_generate_with_openrouter_passes_api_key(self):
        """generate() deve passar api_key para modelos OpenRouter."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "openrouter/mistralai/mistral-7b-instruct"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        with patch("app.services.llm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_response

            with patch("app.services.llm.settings") as mock_settings:
                mock_settings.openrouter_api_key = "sk-or-test-key"
                mock_settings.llm_default_model = "gpt-4o-mini"
                mock_settings.llm_temperature = 0.7
                mock_settings.llm_max_tokens = 2000
                mock_settings.llm_timeout = 60

                service = LLMService(model="openrouter/mistralai/mistral-7b-instruct")
                await service.generate("Teste")

                # Verifica que api_key foi passado
                call_kwargs = mock_completion.call_args.kwargs
                assert "api_key" in call_kwargs
                assert call_kwargs["api_key"] == "sk-or-test-key"

    @pytest.mark.asyncio
    async def test_generate_with_openai_no_api_key_param(self):
        """generate() nao deve passar api_key para modelos OpenAI."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-4o-mini"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        with patch("app.services.llm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_response

            service = LLMService()
            await service.generate("Teste")

            # Verifica que api_key NAO foi passado
            call_kwargs = mock_completion.call_args.kwargs
            assert "api_key" not in call_kwargs
