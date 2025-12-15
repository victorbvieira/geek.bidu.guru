"""
Testes unitarios para modelos relacionados a IA.

Testa:
- AIConfig: Configuracoes de providers, modelos e prompts
- AILog: Log de chamadas ao LLM
- Enums: AIProvider, AIUseCase, AIEntity
"""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.ai_config import (
    AIConfig,
    AIEntity,
    AIProvider,
    AIUseCase,
)
from app.models.ai_log import AILog


# =============================================================================
# Testes de Enums
# =============================================================================


class TestAIProviderEnum:
    """Testes para enum AIProvider."""

    def test_providers_disponiveis(self):
        """Deve ter todos os providers esperados."""
        providers = [p.value for p in AIProvider]
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers
        assert "openrouter" in providers

    def test_provider_values(self):
        """Valores devem ser strings lowercase."""
        for provider in AIProvider:
            assert provider.value == provider.value.lower()
            assert isinstance(provider.value, str)


class TestAIEntityEnum:
    """Testes para enum AIEntity."""

    def test_entidades_disponiveis(self):
        """Deve ter todas as entidades esperadas."""
        entities = [e.value for e in AIEntity]
        assert "post" in entities
        assert "category" in entities
        assert "occasion" in entities
        assert "product" in entities
        assert "general" in entities

    def test_entity_values(self):
        """Valores devem ser strings lowercase."""
        for entity in AIEntity:
            assert entity.value == entity.value.lower()


class TestAIUseCaseEnum:
    """Testes para enum AIUseCase."""

    def test_use_cases_seo_genericos(self):
        """Deve ter casos de uso SEO genericos."""
        use_cases = [uc.value for uc in AIUseCase]
        assert "seo_title" in use_cases
        assert "seo_description" in use_cases
        assert "seo_keywords" in use_cases

    def test_use_cases_post(self):
        """Deve ter casos de uso especificos para Post."""
        use_cases = [uc.value for uc in AIUseCase]
        assert "post_seo_all" in use_cases
        assert "post_seo_keyword" in use_cases
        assert "post_seo_title" in use_cases
        assert "post_seo_description" in use_cases
        assert "post_tags" in use_cases

    def test_use_cases_occasion(self):
        """Deve ter casos de uso especificos para Occasion."""
        use_cases = [uc.value for uc in AIUseCase]
        assert "occasion_seo_all" in use_cases
        assert "occasion_seo_keyword" in use_cases
        assert "occasion_seo_title" in use_cases
        assert "occasion_seo_description" in use_cases
        assert "occasion_content" in use_cases
        assert "occasion_tags" in use_cases

    def test_use_cases_category(self):
        """Deve ter casos de uso especificos para Category."""
        use_cases = [uc.value for uc in AIUseCase]
        assert "category_seo_keyword" in use_cases
        assert "category_seo_title" in use_cases
        assert "category_seo_description" in use_cases
        assert "category_tags" in use_cases

    def test_use_cases_conteudo(self):
        """Deve ter casos de uso para geracao de conteudo."""
        use_cases = [uc.value for uc in AIUseCase]
        assert "post_content" in use_cases
        assert "product_description" in use_cases


# =============================================================================
# Testes do Model AIConfig
# =============================================================================


class TestAIConfigModel:
    """Testes para model AIConfig."""

    def test_aiconfig_creation(self):
        """Deve criar configuracao com atributos corretos."""
        config = AIConfig(
            use_case=AIUseCase.SEO_TITLE,
            name="Titulo SEO",
            description="Gera titulos otimizados para SEO",
            provider=AIProvider.OPENROUTER,
            model="google/gemini-2.0-flash-exp:free",
            system_prompt="Voce e um especialista em SEO...",
            temperature=0.7,
            max_tokens=100,
            is_active=True,
        )
        assert config.use_case == AIUseCase.SEO_TITLE
        assert config.name == "Titulo SEO"
        assert config.provider == AIProvider.OPENROUTER
        assert config.temperature == 0.7
        assert config.max_tokens == 100
        assert config.is_active is True

    def test_aiconfig_default_values(self):
        """Deve usar valores padrao corretos quando passados explicitamente.

        Nota: server_default so e aplicado pelo banco, nao em instancias Python.
        Por isso testamos com valores explicitos.
        """
        config = AIConfig(
            use_case=AIUseCase.SEO_DESCRIPTION,
            name="Descricao SEO",
            model="gpt-4o-mini",
            system_prompt="Voce e um especialista...",
            temperature=0.7,
            max_tokens=500,
            is_active=True,
            provider=AIProvider.OPENROUTER,
        )
        # Verifica que valores foram setados
        assert config.temperature == 0.7
        assert config.max_tokens == 500
        assert config.is_active is True
        assert config.provider == AIProvider.OPENROUTER

    def test_aiconfig_with_user_prompt(self):
        """Deve aceitar user_prompt template."""
        config = AIConfig(
            use_case=AIUseCase.POST_SEO_ALL,
            name="SEO Completo",
            model="gpt-4o-mini",
            system_prompt="Instrucoes...",
            user_prompt="Titulo: {{title}}\nConteudo: {{content}}",
        )
        assert config.user_prompt is not None
        assert "{{title}}" in config.user_prompt
        assert "{{content}}" in config.user_prompt

    def test_aiconfig_repr(self):
        """Deve ter representacao string legivel."""
        config = AIConfig(
            id=uuid4(),
            use_case=AIUseCase.SEO_TITLE,
            name="Test",
            model="gpt-4o-mini",
            system_prompt="Test prompt",
        )
        repr_str = repr(config)
        assert "AIConfig" in repr_str
        assert "seo_title" in repr_str

    def test_aiconfig_full_model_name_openrouter(self):
        """full_model_name deve adicionar prefixo openrouter/."""
        config = AIConfig(
            use_case=AIUseCase.SEO_TITLE,
            name="Test",
            provider=AIProvider.OPENROUTER,
            model="google/gemini-2.0-flash-exp:free",
            system_prompt="Test",
        )
        assert config.full_model_name.startswith("openrouter/")

    def test_aiconfig_full_model_name_openrouter_no_duplicate(self):
        """full_model_name nao deve duplicar prefixo openrouter/."""
        config = AIConfig(
            use_case=AIUseCase.SEO_TITLE,
            name="Test",
            provider=AIProvider.OPENROUTER,
            model="openrouter/google/gemini-2.0-flash",
            system_prompt="Test",
        )
        # Nao deve ter openrouter/openrouter/
        assert "openrouter/openrouter/" not in config.full_model_name

    def test_aiconfig_full_model_name_google(self):
        """full_model_name deve adicionar prefixo gemini/ para Google."""
        config = AIConfig(
            use_case=AIUseCase.SEO_TITLE,
            name="Test",
            provider=AIProvider.GOOGLE,
            model="gemini-1.5-flash",
            system_prompt="Test",
        )
        assert config.full_model_name.startswith("gemini/")

    def test_aiconfig_full_model_name_openai(self):
        """full_model_name deve manter nome direto para OpenAI."""
        config = AIConfig(
            use_case=AIUseCase.SEO_TITLE,
            name="Test",
            provider=AIProvider.OPENAI,
            model="gpt-4o-mini",
            system_prompt="Test",
        )
        assert config.full_model_name == "gpt-4o-mini"

    def test_aiconfig_all_providers(self):
        """Deve suportar todos os providers."""
        for provider in AIProvider:
            config = AIConfig(
                use_case=AIUseCase.SEO_TITLE,
                name=f"Test {provider.value}",
                provider=provider,
                model="test-model",
                system_prompt="Test",
            )
            assert config.provider == provider

    def test_aiconfig_all_use_cases(self):
        """Deve suportar todos os casos de uso."""
        for use_case in AIUseCase:
            config = AIConfig(
                use_case=use_case,
                name=f"Test {use_case.value}",
                model="test-model",
                system_prompt="Test",
            )
            assert config.use_case == use_case

    def test_aiconfig_entity_field(self):
        """Deve suportar campo entity."""
        config = AIConfig(
            use_case=AIUseCase.POST_SEO_ALL,
            name="Test",
            model="test-model",
            system_prompt="Test",
            entity=AIEntity.POST,
        )
        assert config.entity == AIEntity.POST


# =============================================================================
# Testes do Model AILog
# =============================================================================


class TestAILogModel:
    """Testes para model AILog."""

    def test_ailog_creation(self):
        """Deve criar log com atributos corretos."""
        log = AILog(
            use_case="post_tags",
            provider="openrouter",
            model="google/gemini-2.0-flash-exp:free",
            user_prompt="Gere tags para: Titulo do Post",
            system_prompt="Voce e um especialista em SEO...",
            response_content="geek, presentes, natal",
            prompt_tokens=50,
            completion_tokens=20,
            total_tokens=70,
            cost_usd=Decimal("0.000010"),
            latency_ms=1500,
            success=True,
        )
        assert log.use_case == "post_tags"
        assert log.provider == "openrouter"
        assert log.total_tokens == 70
        assert log.cost_usd == Decimal("0.000010")
        assert log.success is True

    def test_ailog_with_entity(self):
        """Deve aceitar entity_type e entity_id."""
        entity_id = uuid4()
        log = AILog(
            use_case="seo_title",
            provider="openai",
            model="gpt-4o-mini",
            user_prompt="Gere titulo",
            entity_type="post",
            entity_id=entity_id,
            success=True,
        )
        assert log.entity_type == "post"
        assert log.entity_id == entity_id

    def test_ailog_with_error(self):
        """Deve registrar erro quando falha."""
        log = AILog(
            use_case="seo_description",
            provider="openai",
            model="gpt-4o-mini",
            user_prompt="Gere descricao",
            success=False,
            error_message="Rate limit exceeded",
        )
        assert log.success is False
        assert log.error_message == "Rate limit exceeded"
        assert log.response_content is None

    def test_ailog_with_user_id(self):
        """Deve aceitar user_id do admin que disparou."""
        user_id = uuid4()
        log = AILog(
            use_case="post_content",
            provider="anthropic",
            model="claude-3-haiku",
            user_prompt="Gere conteudo",
            user_id=user_id,
            success=True,
        )
        assert log.user_id == user_id

    def test_ailog_repr_success(self):
        """Repr deve mostrar status OK para sucesso."""
        log = AILog(
            id=uuid4(),
            use_case="seo_title",
            provider="openai",
            model="gpt-4o-mini",
            user_prompt="Test",
            success=True,
        )
        repr_str = repr(log)
        assert "AILog" in repr_str
        assert "OK" in repr_str
        assert "seo_title" in repr_str

    def test_ailog_repr_error(self):
        """Repr deve mostrar ERRO para falha."""
        log = AILog(
            id=uuid4(),
            use_case="seo_title",
            provider="openai",
            model="gpt-4o-mini",
            user_prompt="Test",
            success=False,
        )
        repr_str = repr(log)
        assert "ERRO" in repr_str

    def test_ailog_default_success(self):
        """Default de success deve ser True quando passado explicitamente.

        Nota: server_default so e aplicado pelo banco, nao em instancias Python.
        """
        log = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
            success=True,
        )
        assert log.success is True

    def test_ailog_cost_precision(self):
        """Custo deve ter precisao de 6 casas decimais."""
        log = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
            cost_usd=Decimal("0.000001"),
        )
        assert log.cost_usd == Decimal("0.000001")

    def test_ailog_optional_fields(self):
        """Campos opcionais devem aceitar None."""
        log = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
        )
        assert log.system_prompt is None
        assert log.response_content is None
        assert log.finish_reason is None
        assert log.prompt_tokens is None
        assert log.completion_tokens is None
        assert log.total_tokens is None
        assert log.cost_usd is None
        assert log.latency_ms is None
        assert log.entity_type is None
        assert log.entity_id is None
        assert log.user_id is None
        assert log.temperature is None
        assert log.max_tokens is None


# =============================================================================
# Testes dos campos AI em Category
# =============================================================================


class TestCategoryAIFields:
    """Testes para campos de IA no model Category."""

    def test_category_ai_fields_defaults(self):
        """Campos AI devem aceitar valores default quando passados.

        Nota: server_default so e aplicado pelo banco, nao em instancias Python.
        Aqui verificamos que os campos aceitam valores zero.
        """
        from app.models.category import Category

        category = Category(
            name="Test Category",
            slug="test-category",
            ai_tokens_used=0,
            ai_prompt_tokens=0,
            ai_completion_tokens=0,
            ai_cost_usd=Decimal("0"),
            ai_generations_count=0,
        )
        # Valores devem ser 0 quando passados explicitamente
        assert category.ai_tokens_used == 0
        assert category.ai_prompt_tokens == 0
        assert category.ai_completion_tokens == 0
        assert category.ai_cost_usd == Decimal("0")
        assert category.ai_generations_count == 0

    def test_category_ai_fields_update(self):
        """Deve permitir atualizar campos AI."""
        from app.models.category import Category

        category = Category(
            name="Test Category",
            slug="test-category",
            ai_tokens_used=150,
            ai_prompt_tokens=100,
            ai_completion_tokens=50,
            ai_cost_usd=Decimal("0.000150"),
            ai_generations_count=3,
        )
        assert category.ai_tokens_used == 150
        assert category.ai_prompt_tokens == 100
        assert category.ai_completion_tokens == 50
        assert category.ai_cost_usd == Decimal("0.000150")
        assert category.ai_generations_count == 3

    def test_category_tags_field(self):
        """Deve suportar campo tags como lista."""
        from app.models.category import Category

        category = Category(
            name="Test Category",
            slug="test-category",
            tags=["geek", "presentes", "natal"],
        )
        assert category.tags == ["geek", "presentes", "natal"]
        assert len(category.tags) == 3

    def test_category_seo_focus_keyword(self):
        """Deve suportar campo seo_focus_keyword."""
        from app.models.category import Category

        category = Category(
            name="Funko Pop",
            slug="funko-pop",
            seo_focus_keyword="funko pop colecao",
        )
        assert category.seo_focus_keyword == "funko pop colecao"


# =============================================================================
# Testes dos campos AI em Occasion
# =============================================================================


class TestOccasionModel:
    """Testes para model Occasion."""

    def test_occasion_creation(self):
        """Deve criar ocasiao com atributos corretos."""
        from app.models.occasion import Occasion

        occasion = Occasion(
            name="Natal",
            slug="natal",
            description="Presentes para o Natal",
            icon="🎄",
            is_active=True,
            display_order=1,
        )
        assert occasion.name == "Natal"
        assert occasion.slug == "natal"
        assert occasion.icon == "🎄"
        assert occasion.is_active is True

    def test_occasion_ai_fields_defaults(self):
        """Campos AI devem aceitar valores default quando passados.

        Nota: server_default so e aplicado pelo banco, nao em instancias Python.
        Aqui verificamos que os campos aceitam valores zero.
        """
        from app.models.occasion import Occasion

        occasion = Occasion(
            name="Test",
            slug="test",
            ai_tokens_used=0,
            ai_prompt_tokens=0,
            ai_completion_tokens=0,
            ai_cost_usd=Decimal("0"),
            ai_generations_count=0,
        )
        assert occasion.ai_tokens_used == 0
        assert occasion.ai_prompt_tokens == 0
        assert occasion.ai_completion_tokens == 0
        assert occasion.ai_cost_usd == Decimal("0")
        assert occasion.ai_generations_count == 0

    def test_occasion_ai_fields_update(self):
        """Deve permitir atualizar campos AI."""
        from app.models.occasion import Occasion

        occasion = Occasion(
            name="Natal",
            slug="natal",
            ai_tokens_used=200,
            ai_prompt_tokens=150,
            ai_completion_tokens=50,
            ai_cost_usd=Decimal("0.000200"),
            ai_generations_count=5,
        )
        assert occasion.ai_tokens_used == 200
        assert occasion.ai_cost_usd == Decimal("0.000200")
        assert occasion.ai_generations_count == 5

    def test_occasion_seo_fields(self):
        """Deve suportar campos SEO."""
        from app.models.occasion import Occasion

        occasion = Occasion(
            name="Dia dos Namorados",
            slug="dia-dos-namorados",
            seo_focus_keyword="presentes dia dos namorados",
            seo_title="Melhores Presentes para Dia dos Namorados 2024",
            seo_description="Encontre os melhores presentes...",
        )
        assert occasion.seo_focus_keyword == "presentes dia dos namorados"
        assert len(occasion.seo_title) <= 60
        assert len(occasion.seo_description) <= 160

    def test_occasion_tags_field(self):
        """Deve suportar campo tags como lista."""
        from app.models.occasion import Occasion

        occasion = Occasion(
            name="Aniversario",
            slug="aniversario",
            tags=["presente", "aniversario", "celebracao"],
        )
        assert occasion.tags == ["presente", "aniversario", "celebracao"]

    def test_occasion_content_field(self):
        """Deve suportar campo content para texto Markdown."""
        from app.models.occasion import Occasion

        content = """
        # Presentes para Aniversário

        O aniversário é uma data especial...
        """
        occasion = Occasion(
            name="Aniversario",
            slug="aniversario",
            content=content,
        )
        assert occasion.content is not None
        assert "Presentes para Aniversário" in occasion.content

    def test_occasion_next_review_date(self):
        """Deve suportar campo next_review_date."""
        from datetime import date

        from app.models.occasion import Occasion

        occasion = Occasion(
            name="Natal",
            slug="natal",
            next_review_date=date(2025, 11, 1),
        )
        assert occasion.next_review_date == date(2025, 11, 1)

    def test_occasion_repr(self):
        """Deve ter representacao string legivel."""
        from app.models.occasion import Occasion

        occasion = Occasion(
            id=uuid4(),
            name="Natal",
            slug="natal",
        )
        repr_str = repr(occasion)
        assert "Occasion" in repr_str
        assert "Natal" in repr_str
        assert "natal" in repr_str
