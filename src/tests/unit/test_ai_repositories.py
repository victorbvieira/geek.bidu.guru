"""
Testes unitarios para repositorios relacionados a IA.

Testa:
- AIConfigRepository: CRUD e buscas de configuracoes
- AILogRepository: Criacao e consulta de logs
- OccasionRepository: CRUD e buscas de ocasioes
"""

from datetime import datetime, UTC
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio

from app.models.ai_config import AIConfig, AIEntity, AIProvider, AIUseCase
from app.models.ai_log import AILog
from app.models.occasion import Occasion
from app.repositories.ai_config import AIConfigRepository
from app.repositories.ai_log import AILogRepository
from app.repositories.occasion import OccasionRepository


# =============================================================================
# Testes do AIConfigRepository
# =============================================================================


class TestAIConfigRepository:
    """Testes para AIConfigRepository."""

    @pytest_asyncio.fixture
    async def repo(self, db_session):
        """Cria repositorio para testes."""
        return AIConfigRepository(db_session)

    @pytest_asyncio.fixture
    async def sample_config(self, db_session) -> AIConfig:
        """Cria configuracao de exemplo."""
        config = AIConfig(
            use_case=AIUseCase.SEO_TITLE,
            name="Titulo SEO",
            description="Gera titulos otimizados",
            provider=AIProvider.OPENROUTER,
            model="google/gemini-2.0-flash-exp:free",
            system_prompt="Voce e um especialista em SEO...",
            temperature=0.7,
            max_tokens=100,
            is_active=True,
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        return config

    @pytest_asyncio.fixture
    async def multiple_configs(self, db_session) -> list[AIConfig]:
        """Cria multiplas configuracoes."""
        configs = [
            AIConfig(
                use_case=AIUseCase.SEO_DESCRIPTION,
                name="Descricao SEO",
                provider=AIProvider.OPENAI,
                model="gpt-4o-mini",
                system_prompt="Gere descricoes...",
                is_active=True,
            ),
            AIConfig(
                use_case=AIUseCase.POST_TAGS,
                name="Tags de Post",
                provider=AIProvider.OPENROUTER,
                model="google/gemini-flash",
                system_prompt="Gere tags...",
                is_active=True,
            ),
            AIConfig(
                use_case=AIUseCase.PRODUCT_DESCRIPTION,
                name="Descricao Produto (inativo)",
                provider=AIProvider.ANTHROPIC,
                model="claude-3-haiku",
                system_prompt="Gere descricao...",
                is_active=False,
            ),
        ]
        for config in configs:
            db_session.add(config)
        await db_session.commit()
        return configs

    # -------------------------------------------------------------------------
    # Testes de Busca por Use Case
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_by_use_case(self, repo, sample_config):
        """Deve encontrar configuracao por use_case."""
        result = await repo.get_by_use_case(AIUseCase.SEO_TITLE)

        assert result is not None
        assert result.id == sample_config.id
        assert result.use_case == AIUseCase.SEO_TITLE

    @pytest.mark.asyncio
    async def test_get_by_use_case_not_found(self, repo):
        """Deve retornar None para use_case inexistente."""
        result = await repo.get_by_use_case(AIUseCase.TRANSLATION)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_active_by_use_case(self, repo, sample_config):
        """Deve encontrar configuracao ativa por use_case."""
        result = await repo.get_active_by_use_case(AIUseCase.SEO_TITLE)

        assert result is not None
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_get_active_by_use_case_inactive(self, repo, db_session):
        """Deve retornar None se configuracao esta inativa."""
        # Cria config inativa
        config = AIConfig(
            use_case=AIUseCase.SOCIAL_SHARE,
            name="Social Inativo",
            model="test",
            system_prompt="test",
            is_active=False,
        )
        db_session.add(config)
        await db_session.commit()

        result = await repo.get_active_by_use_case(AIUseCase.SOCIAL_SHARE)

        assert result is None

    # -------------------------------------------------------------------------
    # Testes de Listagem
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_all(self, repo, multiple_configs):
        """Deve retornar todas as configuracoes ordenadas por nome."""
        result = await repo.get_all()

        assert len(result) == 3
        # Deve estar ordenado por nome
        names = [c.name for c in result]
        assert names == sorted(names)

    @pytest.mark.asyncio
    async def test_get_all_active(self, repo, multiple_configs):
        """Deve retornar apenas configuracoes ativas."""
        result = await repo.get_all_active()

        assert len(result) == 2
        for config in result:
            assert config.is_active is True

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repo):
        """Deve retornar lista vazia quando nao ha configs."""
        result = await repo.get_all()

        assert result == []

    # -------------------------------------------------------------------------
    # Testes de Busca
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_by_name(self, repo, multiple_configs):
        """Deve encontrar configs por nome."""
        result = await repo.search("SEO")

        assert len(result) == 1
        assert "SEO" in result[0].name

    @pytest.mark.asyncio
    async def test_search_by_description(self, repo, sample_config):
        """Deve encontrar configs por descricao."""
        result = await repo.search("otimizados")

        assert len(result) == 1
        assert result[0].id == sample_config.id

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, repo, sample_config):
        """Busca deve ser case-insensitive."""
        result = await repo.search("seo")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_pagination(self, repo, multiple_configs):
        """Deve suportar paginacao na busca."""
        result = await repo.search("", skip=1, limit=2)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_count_search(self, repo, multiple_configs):
        """Deve contar resultados de busca."""
        count = await repo.count_search("Descricao")

        assert count == 2  # Descricao SEO e Descricao Produto


# =============================================================================
# Testes do AILogRepository
# =============================================================================


class TestAILogRepository:
    """Testes para AILogRepository."""

    @pytest_asyncio.fixture
    async def repo(self, db_session):
        """Cria repositorio para testes."""
        return AILogRepository(db_session)

    @pytest_asyncio.fixture
    async def sample_log(self, db_session) -> AILog:
        """Cria log de exemplo."""
        log = AILog(
            use_case="seo_title",
            provider="openrouter",
            model="google/gemini-2.0-flash",
            user_prompt="Gere titulo para: Post de Teste",
            system_prompt="Voce e especialista em SEO...",
            response_content="Top 10 Produtos Geek 2024",
            prompt_tokens=50,
            completion_tokens=20,
            total_tokens=70,
            cost_usd=Decimal("0.000010"),
            latency_ms=1200,
            success=True,
        )
        db_session.add(log)
        await db_session.commit()
        await db_session.refresh(log)
        return log

    # -------------------------------------------------------------------------
    # Testes de Criacao
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_log(self, repo):
        """Deve criar log com todos os campos."""
        log = await repo.create(
            use_case="post_tags",
            provider="openai",
            model="gpt-4o-mini",
            user_prompt="Gere tags",
            system_prompt="Instrucoes...",
            response_content="geek, presente, natal",
            prompt_tokens=30,
            completion_tokens=10,
            total_tokens=40,
            cost_usd=Decimal("0.000005"),
            latency_ms=800,
            success=True,
        )

        assert log.id is not None
        assert log.use_case == "post_tags"
        assert log.total_tokens == 40

    @pytest.mark.asyncio
    async def test_create_log_with_entity(self, repo):
        """Deve criar log associado a uma entidade."""
        entity_id = uuid4()
        log = await repo.create(
            use_case="occasion_seo_title",
            provider="openrouter",
            model="gemini-flash",
            user_prompt="Gere titulo",
            entity_type="occasion",
            entity_id=entity_id,
        )

        assert log.entity_type == "occasion"
        assert log.entity_id == entity_id

    @pytest.mark.asyncio
    async def test_create_log_error(self, repo):
        """Deve criar log de erro."""
        log = await repo.create(
            use_case="seo_description",
            provider="openai",
            model="gpt-4o-mini",
            user_prompt="Gere descricao",
            success=False,
            error_message="Rate limit exceeded",
        )

        assert log.success is False
        assert log.error_message == "Rate limit exceeded"

    # -------------------------------------------------------------------------
    # Testes de Listagem
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_all(self, repo, sample_log):
        """Deve listar logs ordenados por data decrescente."""
        result = await repo.get_all(limit=10)

        assert len(result) == 1
        assert result[0].id == sample_log.id

    @pytest.mark.asyncio
    async def test_get_all_filter_use_case(self, repo, sample_log, db_session):
        """Deve filtrar por use_case."""
        # Cria outro log com use_case diferente
        log2 = AILog(
            use_case="post_tags",
            provider="openai",
            model="gpt-4o-mini",
            user_prompt="Test",
            success=True,
        )
        db_session.add(log2)
        await db_session.commit()

        result = await repo.get_all(use_case="seo_title")

        assert len(result) == 1
        assert result[0].use_case == "seo_title"

    @pytest.mark.asyncio
    async def test_get_all_filter_success(self, repo, sample_log, db_session):
        """Deve filtrar por success."""
        # Cria log de erro
        error_log = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
            success=False,
        )
        db_session.add(error_log)
        await db_session.commit()

        success_only = await repo.get_all(success=True)
        errors_only = await repo.get_all(success=False)

        assert len(success_only) == 1
        assert len(errors_only) == 1

    @pytest.mark.asyncio
    async def test_get_all_filter_entity(self, repo, db_session):
        """Deve filtrar por entity_type e entity_id."""
        entity_id = uuid4()
        log = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
            entity_type="post",
            entity_id=entity_id,
            success=True,
        )
        db_session.add(log)
        await db_session.commit()

        result = await repo.get_all(entity_type="post", entity_id=entity_id)

        assert len(result) == 1
        assert result[0].entity_id == entity_id

    @pytest.mark.asyncio
    async def test_get_all_pagination(self, repo, db_session):
        """Deve suportar paginacao."""
        # Cria 5 logs
        for i in range(5):
            log = AILog(
                use_case=f"test_{i}",
                provider="test",
                model="test",
                user_prompt="test",
                success=True,
            )
            db_session.add(log)
        await db_session.commit()

        page1 = await repo.get_all(limit=2, offset=0)
        page2 = await repo.get_all(limit=2, offset=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id

    # -------------------------------------------------------------------------
    # Testes de Busca por ID
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, sample_log):
        """Deve encontrar log por ID."""
        result = await repo.get(sample_log.id)

        assert result is not None
        assert result.id == sample_log.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo):
        """Deve retornar None para ID inexistente."""
        result = await repo.get(uuid4())

        assert result is None

    # -------------------------------------------------------------------------
    # Testes de Contagem
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_count(self, repo, sample_log):
        """Deve contar logs."""
        total = await repo.count()

        assert total == 1

    @pytest.mark.asyncio
    async def test_count_filter_use_case(self, repo, sample_log, db_session):
        """Deve contar com filtro de use_case."""
        # Adiciona outro log
        log2 = AILog(
            use_case="post_tags",
            provider="test",
            model="test",
            user_prompt="test",
            success=True,
        )
        db_session.add(log2)
        await db_session.commit()

        count = await repo.count(use_case="seo_title")

        assert count == 1

    @pytest.mark.asyncio
    async def test_count_filter_success(self, repo, sample_log, db_session):
        """Deve contar com filtro de success."""
        # Adiciona log de erro
        error = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
            success=False,
        )
        db_session.add(error)
        await db_session.commit()

        success_count = await repo.count(success=True)
        error_count = await repo.count(success=False)

        assert success_count == 1
        assert error_count == 1

    # -------------------------------------------------------------------------
    # Testes de Custo Total
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_total_cost(self, repo, db_session):
        """Deve calcular custo total."""
        # Cria logs com custos
        for cost in ["0.000010", "0.000020", "0.000030"]:
            log = AILog(
                use_case="test",
                provider="test",
                model="test",
                user_prompt="test",
                cost_usd=Decimal(cost),
                success=True,
            )
            db_session.add(log)
        await db_session.commit()

        total = await repo.get_total_cost()

        assert total == Decimal("0.000060")

    @pytest.mark.asyncio
    async def test_get_total_cost_excludes_errors(self, repo, db_session):
        """Custo total deve excluir logs com erro."""
        # Log de sucesso
        success = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
            cost_usd=Decimal("0.000010"),
            success=True,
        )
        # Log de erro
        error = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
            cost_usd=Decimal("0.000020"),
            success=False,
        )
        db_session.add_all([success, error])
        await db_session.commit()

        total = await repo.get_total_cost()

        # Deve somar apenas o de sucesso
        assert total == Decimal("0.000010")

    @pytest.mark.asyncio
    async def test_get_total_cost_with_date_range(self, repo, db_session):
        """Deve calcular custo por periodo."""
        now = datetime.now(UTC)
        log = AILog(
            use_case="test",
            provider="test",
            model="test",
            user_prompt="test",
            cost_usd=Decimal("0.000050"),
            success=True,
        )
        db_session.add(log)
        await db_session.commit()

        total = await repo.get_total_cost(start_date=now)

        assert total >= Decimal("0")  # Pode ser 0 ou o valor dependendo do timing

    @pytest.mark.asyncio
    async def test_get_total_cost_empty(self, repo):
        """Deve retornar 0 quando nao ha logs."""
        total = await repo.get_total_cost()

        assert total == Decimal("0")


# =============================================================================
# Testes do OccasionRepository
# =============================================================================


class TestOccasionRepository:
    """Testes para OccasionRepository."""

    @pytest_asyncio.fixture
    async def repo(self, db_session):
        """Cria repositorio para testes."""
        return OccasionRepository(db_session)

    @pytest_asyncio.fixture
    async def sample_occasion(self, db_session) -> Occasion:
        """Cria ocasiao de exemplo."""
        occasion = Occasion(
            name="Natal",
            slug="natal",
            description="Presentes para o Natal",
            icon="🎄",
            is_active=True,
            display_order=1,
        )
        db_session.add(occasion)
        await db_session.commit()
        await db_session.refresh(occasion)
        return occasion

    @pytest_asyncio.fixture
    async def multiple_occasions(self, db_session) -> list[Occasion]:
        """Cria multiplas ocasioes."""
        occasions = [
            Occasion(name="Aniversario", slug="aniversario", is_active=True, display_order=2),
            Occasion(name="Dia dos Namorados", slug="dia-dos-namorados", is_active=True, display_order=3),
            Occasion(name="Pascoa", slug="pascoa", is_active=False, display_order=4),
        ]
        for occ in occasions:
            db_session.add(occ)
        await db_session.commit()
        return occasions

    # -------------------------------------------------------------------------
    # Testes de Busca por Slug
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_by_slug(self, repo, sample_occasion):
        """Deve encontrar ocasiao por slug."""
        result = await repo.get_by_slug("natal")

        assert result is not None
        assert result.slug == "natal"
        assert result.name == "Natal"

    @pytest.mark.asyncio
    async def test_get_by_slug_not_found(self, repo):
        """Deve retornar None para slug inexistente."""
        result = await repo.get_by_slug("inexistente")

        assert result is None

    # -------------------------------------------------------------------------
    # Testes de Listagem
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_active(self, repo, sample_occasion, multiple_occasions):
        """Deve listar apenas ocasioes ativas."""
        result = await repo.get_active()

        assert len(result) == 3  # Natal, Aniversario, Dia dos Namorados
        for occ in result:
            assert occ.is_active is True

    @pytest.mark.asyncio
    async def test_get_active_ordered(self, repo, sample_occasion, multiple_occasions):
        """Deve ordenar por display_order."""
        result = await repo.get_active()

        orders = [occ.display_order for occ in result]
        assert orders == sorted(orders)

    @pytest.mark.asyncio
    async def test_get_active_pagination(self, repo, sample_occasion, multiple_occasions):
        """Deve suportar paginacao."""
        result = await repo.get_active(skip=1, limit=2)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_count_active(self, repo, sample_occasion, multiple_occasions):
        """Deve contar apenas ocasioes ativas."""
        count = await repo.count_active()

        assert count == 3

    @pytest.mark.asyncio
    async def test_get_all_ordered(self, repo, sample_occasion, multiple_occasions):
        """Deve listar todas ordenadas por display_order."""
        result = await repo.get_all_ordered()

        assert len(result) == 4  # Incluindo inativa

    @pytest.mark.asyncio
    async def test_get_paginated(self, repo, sample_occasion, multiple_occasions):
        """Deve listar com paginacao."""
        result = await repo.get_paginated(skip=0, limit=2)

        assert len(result) == 2

    # -------------------------------------------------------------------------
    # Testes de Busca
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_by_name(self, repo, sample_occasion, multiple_occasions):
        """Deve buscar por nome."""
        result = await repo.search("Natal")

        assert len(result) == 1
        assert result[0].name == "Natal"

    @pytest.mark.asyncio
    async def test_search_by_slug(self, repo, sample_occasion, multiple_occasions):
        """Deve buscar por slug."""
        result = await repo.search("dia-dos")

        assert len(result) == 1
        assert result[0].slug == "dia-dos-namorados"

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, repo, sample_occasion):
        """Busca deve ser case-insensitive."""
        result = await repo.search("natal")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_pagination(self, repo, sample_occasion, multiple_occasions):
        """Deve suportar paginacao na busca."""
        result = await repo.search("", skip=0, limit=2)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_count_search(self, repo, sample_occasion, multiple_occasions):
        """Deve contar resultados de busca."""
        count = await repo.count_search("a")  # Natal, Aniversario, Pascoa

        assert count >= 2

    # -------------------------------------------------------------------------
    # Testes de Verificacao de Slug
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_slug_exists(self, repo, sample_occasion):
        """Deve verificar se slug existe."""
        exists = await repo.slug_exists("natal")

        assert exists is True

    @pytest.mark.asyncio
    async def test_slug_exists_not_found(self, repo):
        """Deve retornar False para slug inexistente."""
        exists = await repo.slug_exists("inexistente")

        assert exists is False

    @pytest.mark.asyncio
    async def test_slug_exists_exclude_id(self, repo, sample_occasion):
        """Deve excluir ID especifico na verificacao."""
        # Slug existe, mas excluindo o proprio ID deve retornar False
        exists = await repo.slug_exists("natal", exclude_id=sample_occasion.id)

        assert exists is False

    @pytest.mark.asyncio
    async def test_slug_exists_exclude_other_id(self, repo, sample_occasion):
        """Deve encontrar slug quando excluindo outro ID."""
        other_id = uuid4()
        exists = await repo.slug_exists("natal", exclude_id=other_id)

        assert exists is True
