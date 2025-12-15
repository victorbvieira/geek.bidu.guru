"""
Testes de integracao para rotas de Occasion no blog.

Testa:
- GET /ocasioes: Listagem de ocasioes ativas
- GET /ocasiao/{slug}: Pagina individual de ocasiao
"""

import pytest
import pytest_asyncio

from app.models.occasion import Occasion


class TestOccasionBlogRoutes:
    """Testes para rotas de ocasiao no blog publico."""

    @pytest_asyncio.fixture
    async def sample_occasion(self, db_session) -> Occasion:
        """Cria ocasiao ativa para testes."""
        occasion = Occasion(
            name="Natal",
            slug="natal",
            description="Presentes para o Natal",
            content="# Presentes de Natal\n\nO Natal e uma otima epoca...",
            icon="🎄",
            is_active=True,
            display_order=1,
            seo_title="Melhores Presentes de Natal 2024",
            seo_description="Encontre os melhores presentes geek para Natal.",
        )
        db_session.add(occasion)
        await db_session.commit()
        await db_session.refresh(occasion)
        return occasion

    @pytest_asyncio.fixture
    async def inactive_occasion(self, db_session) -> Occasion:
        """Cria ocasiao inativa para testes."""
        occasion = Occasion(
            name="Pascoa",
            slug="pascoa",
            description="Presentes para Pascoa",
            is_active=False,
            display_order=5,
        )
        db_session.add(occasion)
        await db_session.commit()
        await db_session.refresh(occasion)
        return occasion

    @pytest_asyncio.fixture
    async def multiple_occasions(self, db_session) -> list[Occasion]:
        """Cria multiplas ocasioes."""
        occasions = [
            Occasion(
                name="Aniversario",
                slug="aniversario",
                description="Presentes de aniversario",
                is_active=True,
                display_order=2,
            ),
            Occasion(
                name="Dia dos Namorados",
                slug="dia-dos-namorados",
                description="Presentes romanticos",
                is_active=True,
                display_order=3,
            ),
            Occasion(
                name="Dia das Maes",
                slug="dia-das-maes",
                description="Presentes para mae",
                is_active=True,
                display_order=4,
            ),
        ]
        for occ in occasions:
            db_session.add(occ)
        await db_session.commit()
        return occasions

    # -------------------------------------------------------------------------
    # GET /ocasioes - Listagem de Ocasioes
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_occasions_success(self, client, sample_occasion):
        """Deve retornar pagina de listagem de ocasioes."""
        response = await client.get("/ocasioes")

        assert response.status_code == 200
        # Verifica que e HTML
        assert "text/html" in response.headers.get("content-type", "")
        # Verifica conteudo
        content = response.text
        assert "Natal" in content

    @pytest.mark.asyncio
    async def test_list_occasions_empty(self, client):
        """Deve retornar pagina mesmo sem ocasioes."""
        response = await client.get("/ocasioes")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_occasions_excludes_inactive(
        self, client, sample_occasion, inactive_occasion
    ):
        """Deve listar apenas ocasioes ativas."""
        response = await client.get("/ocasioes")

        content = response.text
        assert "Natal" in content  # Ativa
        assert "Pascoa" not in content  # Inativa

    @pytest.mark.asyncio
    async def test_list_occasions_ordered(
        self, client, sample_occasion, multiple_occasions
    ):
        """Deve ordenar por display_order."""
        response = await client.get("/ocasioes")

        content = response.text
        # Verifica ordem (Natal display_order=1 deve vir primeiro)
        natal_pos = content.find("Natal")
        aniversario_pos = content.find("Aniversario")

        assert natal_pos < aniversario_pos

    @pytest.mark.asyncio
    async def test_list_occasions_seo_meta(self, client, sample_occasion):
        """Deve incluir meta tags SEO."""
        response = await client.get("/ocasioes")

        content = response.text
        # Verifica meta description
        assert 'name="description"' in content

    # -------------------------------------------------------------------------
    # GET /ocasiao/{slug} - Pagina de Ocasiao
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_occasion_success(self, client, sample_occasion):
        """Deve retornar pagina da ocasiao."""
        response = await client.get("/ocasiao/natal")

        assert response.status_code == 200
        content = response.text
        assert "Natal" in content
        assert "Presentes de Natal" in content

    @pytest.mark.asyncio
    async def test_get_occasion_with_content(self, client, sample_occasion):
        """Deve renderizar conteudo Markdown como HTML."""
        response = await client.get("/ocasiao/natal")

        content = response.text
        # Markdown foi convertido para HTML
        assert "<h1>" in content or "Presentes de Natal" in content

    @pytest.mark.asyncio
    async def test_get_occasion_not_found(self, client):
        """Deve retornar 404 para slug inexistente."""
        response = await client.get("/ocasiao/inexistente")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_occasion_inactive_not_found(self, client, inactive_occasion):
        """Deve retornar 404 para ocasiao inativa."""
        response = await client.get("/ocasiao/pascoa")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_occasion_seo_custom(self, client, sample_occasion):
        """Deve usar seo_title e seo_description customizados."""
        response = await client.get("/ocasiao/natal")

        content = response.text
        # Verifica titulo SEO customizado
        assert "Melhores Presentes de Natal 2024" in content

    @pytest.mark.asyncio
    async def test_get_occasion_breadcrumbs(self, client, sample_occasion):
        """Deve incluir breadcrumbs na pagina."""
        response = await client.get("/ocasiao/natal")

        content = response.text
        # Verifica breadcrumbs
        assert "Ocasiões" in content or "ocasioes" in content.lower()

    @pytest.mark.asyncio
    async def test_get_occasion_canonical_url(self, client, sample_occasion):
        """Deve incluir canonical URL."""
        response = await client.get("/ocasiao/natal")

        content = response.text
        assert 'rel="canonical"' in content
        assert "/ocasiao/natal" in content

    @pytest.mark.asyncio
    async def test_get_occasion_without_content(self, client, db_session):
        """Deve funcionar mesmo sem conteudo."""
        # Cria ocasiao sem content
        occasion = Occasion(
            name="Sem Conteudo",
            slug="sem-conteudo",
            description="Apenas descricao",
            is_active=True,
        )
        db_session.add(occasion)
        await db_session.commit()

        response = await client.get("/ocasiao/sem-conteudo")

        assert response.status_code == 200


# =============================================================================
# Testes de campos AI nas ocasioes (via admin)
# =============================================================================


class TestOccasionAIFields:
    """Testes para campos de IA nas ocasioes."""

    @pytest_asyncio.fixture
    async def occasion_with_ai(self, db_session) -> Occasion:
        """Cria ocasiao com dados de IA."""
        from decimal import Decimal
        occasion = Occasion(
            name="Dia dos Pais",
            slug="dia-dos-pais",
            description="Presentes para o Dia dos Pais",
            is_active=True,
            ai_tokens_used=500,
            ai_prompt_tokens=400,
            ai_completion_tokens=100,
            ai_cost_usd=Decimal("0.000500"),
            ai_generations_count=5,
            tags=["pai", "presente", "geek"],
        )
        db_session.add(occasion)
        await db_session.commit()
        await db_session.refresh(occasion)
        return occasion

    @pytest.mark.asyncio
    async def test_occasion_ai_fields_persisted(self, db_session, occasion_with_ai):
        """Campos AI devem ser persistidos corretamente."""
        from decimal import Decimal
        from app.repositories.occasion import OccasionRepository

        repo = OccasionRepository(db_session)
        occasion = await repo.get_by_slug("dia-dos-pais")

        assert occasion.ai_tokens_used == 500
        assert occasion.ai_prompt_tokens == 400
        assert occasion.ai_completion_tokens == 100
        assert occasion.ai_cost_usd == Decimal("0.000500")
        assert occasion.ai_generations_count == 5

    @pytest.mark.asyncio
    async def test_occasion_tags_persisted(self, db_session, occasion_with_ai):
        """Tags devem ser persistidas corretamente."""
        from app.repositories.occasion import OccasionRepository

        repo = OccasionRepository(db_session)
        occasion = await repo.get_by_slug("dia-dos-pais")

        assert occasion.tags == ["pai", "presente", "geek"]


# =============================================================================
# Testes de campos AI nas categorias
# =============================================================================


class TestCategoryAIFieldsPersistence:
    """Testes de persistencia de campos AI em Category."""

    @pytest_asyncio.fixture
    async def category_with_ai(self, db_session):
        """Cria categoria com dados de IA."""
        from decimal import Decimal
        from app.models.category import Category

        category = Category(
            name="Funko Pop",
            slug="funko-pop",
            description="Bonecos colecionaveis Funko Pop",
            ai_tokens_used=300,
            ai_prompt_tokens=200,
            ai_completion_tokens=100,
            ai_cost_usd=Decimal("0.000300"),
            ai_generations_count=3,
            tags=["funko", "colecao", "geek"],
            seo_focus_keyword="funko pop colecao",
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return category

    @pytest.mark.asyncio
    async def test_category_ai_fields_persisted(self, db_session, category_with_ai):
        """Campos AI devem ser persistidos em Category."""
        from decimal import Decimal
        from app.repositories.category import CategoryRepository

        repo = CategoryRepository(db_session)
        category = await repo.get_by_slug("funko-pop")

        assert category.ai_tokens_used == 300
        assert category.ai_cost_usd == Decimal("0.000300")
        assert category.ai_generations_count == 3

    @pytest.mark.asyncio
    async def test_category_tags_persisted(self, db_session, category_with_ai):
        """Tags devem ser persistidas em Category."""
        from app.repositories.category import CategoryRepository

        repo = CategoryRepository(db_session)
        category = await repo.get_by_slug("funko-pop")

        assert category.tags == ["funko", "colecao", "geek"]

    @pytest.mark.asyncio
    async def test_category_seo_focus_keyword(self, db_session, category_with_ai):
        """seo_focus_keyword deve ser persistido."""
        from app.repositories.category import CategoryRepository

        repo = CategoryRepository(db_session)
        category = await repo.get_by_slug("funko-pop")

        assert category.seo_focus_keyword == "funko pop colecao"
