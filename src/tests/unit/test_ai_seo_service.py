"""
Testes unitarios para o servico de geracao de SEO com IA.

Testa:
- AISEOService: Geracao de titulos, descricoes e keywords
- calculate_cost: Calculo de custo baseado em tokens
- Substituicao de placeholders em prompts
"""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from app.models.ai_config import AIConfig, AIEntity, AIProvider, AIUseCase
from app.services.ai_seo import AISEOService, calculate_cost


# =============================================================================
# Testes da funcao calculate_cost
# =============================================================================


class TestCalculateCost:
    """Testes para funcao de calculo de custo."""

    def test_calculate_cost_gpt4o_mini(self):
        """Deve calcular custo corretamente para gpt-4o-mini."""
        # gpt-4o-mini: $0.15 input, $0.60 output per 1M tokens
        cost = calculate_cost("gpt-4o-mini", prompt_tokens=1000, completion_tokens=500)

        # (1000/1M * 0.15) + (500/1M * 0.60) = 0.00015 + 0.0003 = 0.00045
        expected = Decimal("0.00045")
        assert cost == expected

    def test_calculate_cost_gemini_flash(self):
        """Deve calcular custo para modelos Gemini."""
        # gemini-2.0-flash: $0.10 input, $0.40 output per 1M tokens
        cost = calculate_cost("gemini-2.0-flash", prompt_tokens=1000, completion_tokens=1000)

        # (1000/1M * 0.10) + (1000/1M * 0.40) = 0.0001 + 0.0004 = 0.0005
        expected = Decimal("0.0005")
        assert cost == expected

    def test_calculate_cost_openrouter_prefix(self):
        """Deve remover prefixo openrouter/ do nome do modelo."""
        cost1 = calculate_cost("openrouter/google/gemini-2.0-flash", 1000, 1000)
        cost2 = calculate_cost("gemini-2.0-flash", 1000, 1000)

        assert cost1 == cost2

    def test_calculate_cost_model_with_suffix(self):
        """Deve remover sufixo :free do nome do modelo."""
        cost1 = calculate_cost("gemini-2.0-flash:free", 1000, 1000)
        cost2 = calculate_cost("gemini-2.0-flash", 1000, 1000)

        assert cost1 == cost2

    def test_calculate_cost_unknown_model(self):
        """Deve usar preco default para modelo desconhecido."""
        # Default: $1.00 input, $3.00 output per 1M tokens
        cost = calculate_cost("modelo-desconhecido", prompt_tokens=1000, completion_tokens=1000)

        # (1000/1M * 1.00) + (1000/1M * 3.00) = 0.001 + 0.003 = 0.004
        expected = Decimal("0.004")
        assert cost == expected

    def test_calculate_cost_zero_tokens(self):
        """Deve retornar 0 quando nao ha tokens."""
        cost = calculate_cost("gpt-4o-mini", prompt_tokens=0, completion_tokens=0)

        assert cost == Decimal("0")

    def test_calculate_cost_precision(self):
        """Deve ter precisao de 6 casas decimais."""
        cost = calculate_cost("gpt-4o-mini", prompt_tokens=1, completion_tokens=1)

        # Valor muito pequeno deve ter 6 casas
        assert cost == cost.quantize(Decimal("0.000001"))

    def test_calculate_cost_large_tokens(self):
        """Deve calcular corretamente para muitos tokens."""
        cost = calculate_cost("gpt-4o-mini", prompt_tokens=100000, completion_tokens=50000)

        # (100000/1M * 0.15) + (50000/1M * 0.60) = 0.015 + 0.03 = 0.045
        expected = Decimal("0.045")
        assert cost == expected


# =============================================================================
# Testes do AISEOService
# =============================================================================


class TestAISEOService:
    """Testes para o servico de geracao de SEO."""

    @pytest_asyncio.fixture
    async def mock_db_session(self):
        """Mock da sessao de banco."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def service(self, mock_db_session):
        """Cria instancia do servico."""
        return AISEOService(mock_db_session)

    @pytest_asyncio.fixture
    def sample_config(self):
        """Configuracao de exemplo."""
        return AIConfig(
            use_case=AIUseCase.SEO_TITLE,
            name="Titulo SEO",
            provider=AIProvider.OPENROUTER,
            model="google/gemini-2.0-flash-exp:free",
            system_prompt="Voce e um especialista em SEO para blogs geek.",
            user_prompt="Gere um titulo SEO para: {{title}}",
            temperature=0.7,
            max_tokens=100,
            is_active=True,
        )

    # -------------------------------------------------------------------------
    # Testes de Geracao
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_generate_success(self, service, sample_config):
        """Deve gerar conteudo com sucesso."""
        # Mock do repositorio
        with patch.object(service.repo, "get_active_by_use_case", return_value=sample_config):
            # Mock do LLMService
            mock_response = MagicMock()
            mock_response.content = "Top 10 Presentes Geek para 2024"
            mock_response.model = "google/gemini-2.0-flash-exp:free"
            mock_response.usage = {
                "prompt_tokens": 50,
                "completion_tokens": 15,
                "total_tokens": 65,
            }
            mock_response.finish_reason = "stop"

            with patch("app.services.ai_seo.LLMService") as MockLLM:
                mock_llm = AsyncMock()
                mock_llm.generate.return_value = mock_response
                MockLLM.return_value = mock_llm

                result = await service.generate(
                    AIUseCase.SEO_TITLE,
                    title="Presentes Geek 2024",
                )

        assert result["generated_content"] == "Top 10 Presentes Geek para 2024"
        assert result["model_used"] == "google/gemini-2.0-flash-exp:free"
        assert result["tokens_used"] == 65
        assert result["prompt_tokens"] == 50
        assert result["completion_tokens"] == 15

    @pytest.mark.asyncio
    async def test_generate_no_config(self, service):
        """Deve lancar erro quando configuracao nao existe."""
        with patch.object(service.repo, "get_active_by_use_case", return_value=None):
            with pytest.raises(ValueError) as exc_info:
                await service.generate(AIUseCase.TRANSLATION, title="Test")

            assert "Nenhuma configuracao ativa" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_with_cost_calculation(self, service, sample_config):
        """Deve calcular custo na resposta."""
        with patch.object(service.repo, "get_active_by_use_case", return_value=sample_config):
            mock_response = MagicMock()
            mock_response.content = "Titulo gerado"
            mock_response.model = "gpt-4o-mini"
            mock_response.usage = {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            }
            mock_response.finish_reason = "stop"

            with patch("app.services.ai_seo.LLMService") as MockLLM:
                mock_llm = AsyncMock()
                mock_llm.generate.return_value = mock_response
                MockLLM.return_value = mock_llm

                result = await service.generate(
                    AIUseCase.SEO_TITLE,
                    title="Test",
                )

        assert "cost_usd" in result
        assert result["cost_usd"] > 0

    # -------------------------------------------------------------------------
    # Testes de Substituicao de Placeholders
    # -------------------------------------------------------------------------

    def test_replace_placeholders_title(self, service):
        """Deve substituir placeholder {{title}}."""
        template = "Gere titulo para: {{title}}"
        result = service._replace_placeholders(template, title="Meu Post")

        assert result == "Gere titulo para: Meu Post"

    def test_replace_placeholders_content(self, service):
        """Deve substituir placeholder {{content}}."""
        template = "Analise: {{content}}"
        result = service._replace_placeholders(template, content="Conteudo do post")

        assert result == "Analise: Conteudo do post"

    def test_replace_placeholders_content_limit(self, service):
        """Deve limitar content a 5000 caracteres."""
        template = "{{content}}"
        long_content = "A" * 10000
        result = service._replace_placeholders(template, content=long_content)

        assert len(result) == 5000

    def test_replace_placeholders_keywords(self, service):
        """Deve substituir placeholder {{keywords}} com lista."""
        template = "Keywords: {{keywords}}"
        result = service._replace_placeholders(
            template,
            keywords=["geek", "presentes", "natal"],
        )

        assert result == "Keywords: geek, presentes, natal"

    def test_replace_placeholders_product(self, service):
        """Deve substituir placeholders de produto."""
        template = "Produto: {{product_name}} - R$ {{price}} - {{platform}}"
        result = service._replace_placeholders(
            template,
            product_name="Funko Pop",
            price="149.90",
            platform="amazon",
        )

        assert result == "Produto: Funko Pop - R$ 149.90 - amazon"

    def test_replace_placeholders_occasion(self, service):
        """Deve substituir placeholders de ocasiao."""
        template = "Ocasiao: {{occasion_name}} ({{occasion_date}})"
        result = service._replace_placeholders(
            template,
            occasion_name="Natal",
            occasion_date="25/12",
        )

        assert result == "Ocasiao: Natal (25/12)"

    def test_replace_placeholders_extra_context(self, service):
        """Deve substituir placeholders extras customizados."""
        template = "Custom: {{campo_custom}}"
        result = service._replace_placeholders(
            template,
            extra_context={"campo_custom": "valor customizado"},
        )

        assert result == "Custom: valor customizado"

    def test_replace_placeholders_none_values(self, service):
        """Deve substituir None por string vazia."""
        template = "Titulo: {{title}}\nCategoria: {{category}}"
        result = service._replace_placeholders(template, title="Test", category=None)

        assert "Titulo: Test" in result

    # -------------------------------------------------------------------------
    # Testes de Metodos de Conveniencia
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_generate_seo_title(self, service, sample_config):
        """Deve gerar titulo SEO."""
        with patch.object(service, "generate") as mock_generate:
            mock_generate.return_value = {
                "generated_content": "Titulo SEO Gerado",
                "model_used": "gpt-4o-mini",
            }

            result = await service.generate_seo_title(
                title="Meu Post",
                content="Conteudo aqui",
            )

        assert result == "Titulo SEO Gerado"
        mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_seo_description(self, service, sample_config):
        """Deve gerar meta description."""
        with patch.object(service, "generate") as mock_generate:
            mock_generate.return_value = {
                "generated_content": "Descricao meta gerada com 120 caracteres...",
                "model_used": "gpt-4o-mini",
            }

            result = await service.generate_seo_description(
                title="Meu Post",
                category="Geek",
            )

        assert result == "Descricao meta gerada com 120 caracteres..."

    @pytest.mark.asyncio
    async def test_generate_seo_keywords(self, service, sample_config):
        """Deve gerar lista de keywords."""
        with patch.object(service, "generate") as mock_generate:
            mock_generate.return_value = {
                "generated_content": "geek, presentes, natal, funko",
                "model_used": "gpt-4o-mini",
            }

            result = await service.generate_seo_keywords(
                title="Presentes Geek",
            )

        assert isinstance(result, list)
        assert "geek" in result
        assert "presentes" in result

    @pytest.mark.asyncio
    async def test_generate_seo_keywords_newline_separated(self, service):
        """Deve aceitar keywords separadas por quebra de linha."""
        with patch.object(service, "generate") as mock_generate:
            mock_generate.return_value = {
                "generated_content": "geek\npresentes\nnatal",
                "model_used": "gpt-4o-mini",
            }

            result = await service.generate_seo_keywords(title="Test")

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_generate_product_description(self, service):
        """Deve gerar descricao de produto."""
        with patch.object(service, "generate") as mock_generate:
            mock_generate.return_value = {
                "generated_content": "CURTA: Descricao curta aqui. LONGA: Descricao longa e detalhada.",
                "model_used": "gpt-4o-mini",
            }

            result = await service.generate_product_description(
                product_name="Funko Pop Vader",
                category="Star Wars",
                price=149.90,
            )

        assert "short_description" in result
        assert "long_description" in result
        assert "model_used" in result

    @pytest.mark.asyncio
    async def test_generate_product_description_no_structure(self, service):
        """Deve tratar descricao sem estrutura CURTA/LONGA."""
        with patch.object(service, "generate") as mock_generate:
            mock_generate.return_value = {
                "generated_content": "Primeiro paragrafo.\n\nSegundo paragrafo com mais detalhes.",
                "model_used": "gpt-4o-mini",
            }

            result = await service.generate_product_description(
                product_name="Test Product",
            )

        # Deve usar primeiro paragrafo como short
        assert len(result["short_description"]) <= 150

    # -------------------------------------------------------------------------
    # Testes de Build User Prompt (fallback)
    # -------------------------------------------------------------------------

    def test_build_user_prompt_seo_title(self, service):
        """Deve construir prompt para SEO title."""
        prompt = service._build_user_prompt(
            use_case=AIUseCase.SEO_TITLE,
            title="Meu Post",
            content=None,
            keywords=None,
            category=None,
            product_name=None,
            target_audience=None,
        )

        assert "titulo seo" in prompt.lower()
        assert "Meu Post" in prompt

    def test_build_user_prompt_seo_description(self, service):
        """Deve construir prompt para SEO description."""
        prompt = service._build_user_prompt(
            use_case=AIUseCase.SEO_DESCRIPTION,
            title="Meu Post",
            content="Conteudo aqui",
            keywords=None,
            category=None,
            product_name=None,
            target_audience=None,
        )

        assert "description" in prompt.lower()
        assert "Conteudo aqui" in prompt

    def test_build_user_prompt_with_all_fields(self, service):
        """Deve incluir todos os campos fornecidos."""
        prompt = service._build_user_prompt(
            use_case=AIUseCase.PRODUCT_DESCRIPTION,
            title="Titulo",
            content="Conteudo",
            keywords=["key1", "key2"],
            category="Categoria X",
            product_name="Produto Y",
            target_audience="Geeks",
        )

        assert "Categoria X" in prompt
        assert "Produto Y" in prompt
        assert "key1" in prompt
        assert "Geeks" in prompt

    def test_build_user_prompt_content_limit(self, service):
        """Deve limitar conteudo a 5000 caracteres no prompt."""
        long_content = "A" * 10000
        prompt = service._build_user_prompt(
            use_case=AIUseCase.SEO_TITLE,
            title="Test",
            content=long_content,
            keywords=None,
            category=None,
            product_name=None,
            target_audience=None,
        )

        # Conteudo no prompt deve estar limitado
        assert len(prompt) < 10000


# =============================================================================
# Testes de Schemas de AI Config
# =============================================================================


class TestAIConfigSchemas:
    """Testes para schemas Pydantic de AIConfig."""

    def test_ai_config_create_valid(self):
        """Deve criar schema com dados validos."""
        from app.schemas.ai_config import AIConfigCreate

        config = AIConfigCreate(
            use_case=AIUseCase.SEO_TITLE,
            name="Titulo SEO",
            provider=AIProvider.OPENROUTER,
            model="google/gemini-2.0-flash",
            system_prompt="Voce e um especialista em SEO para blogs.",
            temperature=0.7,
            max_tokens=100,
        )

        assert config.use_case == AIUseCase.SEO_TITLE
        assert config.temperature == 0.7

    def test_ai_config_create_defaults(self):
        """Deve usar defaults corretos."""
        from app.schemas.ai_config import AIConfigCreate

        config = AIConfigCreate(
            use_case=AIUseCase.SEO_DESCRIPTION,
            name="Test",
            model="gpt-4o-mini",
            system_prompt="Instructions here...",
        )

        assert config.provider == AIProvider.OPENROUTER
        assert config.temperature == 0.7
        assert config.max_tokens == 500
        assert config.is_active is True

    def test_ai_config_create_temperature_validation(self):
        """Deve validar temperatura entre 0 e 2."""
        from pydantic import ValidationError

        from app.schemas.ai_config import AIConfigCreate

        with pytest.raises(ValidationError):
            AIConfigCreate(
                use_case=AIUseCase.SEO_TITLE,
                name="Test",
                model="test",
                system_prompt="test test test",
                temperature=2.5,  # Invalido: > 2.0
            )

    def test_ai_config_create_max_tokens_validation(self):
        """Deve validar max_tokens entre 50 e 8000."""
        from pydantic import ValidationError

        from app.schemas.ai_config import AIConfigCreate

        with pytest.raises(ValidationError):
            AIConfigCreate(
                use_case=AIUseCase.SEO_TITLE,
                name="Test",
                model="test",
                system_prompt="test test test",
                max_tokens=10,  # Invalido: < 50
            )

    def test_ai_config_update_partial(self):
        """Deve permitir atualizacao parcial."""
        from app.schemas.ai_config import AIConfigUpdate

        update = AIConfigUpdate(name="Novo Nome")

        assert update.name == "Novo Nome"
        assert update.temperature is None
        assert update.model is None

    def test_seo_generate_request(self):
        """Deve criar requisicao de geracao valida."""
        from app.schemas.ai_config import SEOGenerateRequest

        request = SEOGenerateRequest(
            use_case=AIUseCase.POST_SEO_ALL,
            title="Meu Post",
            content="Conteudo aqui",
            keywords=["geek", "presentes"],
            category="Geek",
        )

        assert request.use_case == AIUseCase.POST_SEO_ALL
        assert request.keywords == ["geek", "presentes"]

    def test_seo_generate_response(self):
        """Deve criar resposta de geracao valida."""
        from app.schemas.ai_config import SEOGenerateResponse

        response = SEOGenerateResponse(
            use_case=AIUseCase.SEO_TITLE,
            generated_content="Titulo SEO Gerado",
            model_used="gpt-4o-mini",
            tokens_used=65,
        )

        assert response.generated_content == "Titulo SEO Gerado"
        assert response.tokens_used == 65
