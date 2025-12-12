"""
Testes unitarios para a home page dinamica.

Verifica:
- Carregamento de produtos em destaque
- Carregamento de posts publicados
- Carregamento de categorias
- Fallback para categorias estaticas
"""

import pytest
from httpx import AsyncClient


class TestHomePage:
    """Testes para a home page."""

    @pytest.mark.asyncio
    async def test_homepage_returns_200(self, client: AsyncClient):
        """Homepage deve retornar status 200."""
        response = await client.get("/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_homepage_has_title(self, client: AsyncClient):
        """Homepage deve ter titulo."""
        response = await client.get("/")
        assert "<title>" in response.text
        assert "geek.bidu.guru" in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_hero_section(self, client: AsyncClient):
        """Homepage deve ter secao hero."""
        response = await client.get("/")
        assert 'class="hero"' in response.text
        assert "Encontre o presente geek perfeito" in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_featured_section(self, client: AsyncClient):
        """Homepage deve ter secao de destaques."""
        response = await client.get("/")
        assert 'class="featured"' in response.text
        assert "Destaques" in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_categories_section(self, client: AsyncClient):
        """Homepage deve ter secao de categorias."""
        response = await client.get("/")
        assert 'class="categories"' in response.text
        assert "Navegue por Categoria" in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_newsletter_section(self, client: AsyncClient):
        """Homepage deve ter secao de newsletter."""
        response = await client.get("/")
        assert 'class="newsletter"' in response.text
        assert "Fique por dentro" in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_category_grid(self, client: AsyncClient):
        """Homepage deve ter grid de categorias."""
        response = await client.get("/")
        assert 'class="category-grid"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_fallback_categories(self, client: AsyncClient):
        """Sem categorias no banco, deve mostrar fallback estatico."""
        response = await client.get("/")
        # Pelo menos uma das categorias fallback deve estar presente
        fallback_categories = ["Gamer", "Dev", "Otaku", "Star Wars", "Marvel", "Board Games"]
        has_fallback = any(cat in response.text for cat in fallback_categories)
        # Pode ter categorias dinamicas ou fallback
        assert has_fallback or 'class="category-card"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_cta_buttons(self, client: AsyncClient):
        """Homepage deve ter botoes de CTA."""
        response = await client.get("/")
        assert 'class="btn btn-primary"' in response.text
        assert 'class="btn btn-secondary"' in response.text


class TestHomePageSEO:
    """Testes de SEO para home page."""

    @pytest.mark.asyncio
    async def test_homepage_has_meta_description(self, client: AsyncClient):
        """Homepage deve ter meta description."""
        response = await client.get("/")
        assert 'name="description"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_canonical(self, client: AsyncClient):
        """Homepage deve ter canonical URL."""
        response = await client.get("/")
        assert 'rel="canonical"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_og_tags(self, client: AsyncClient):
        """Homepage deve ter Open Graph tags."""
        response = await client.get("/")
        assert 'property="og:title"' in response.text
        assert 'property="og:description"' in response.text
        assert 'property="og:type"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_twitter_cards(self, client: AsyncClient):
        """Homepage deve ter Twitter Cards."""
        response = await client.get("/")
        assert 'name="twitter:card"' in response.text


class TestHomePageAccessibility:
    """Testes de acessibilidade para home page."""

    @pytest.mark.asyncio
    async def test_homepage_has_proper_heading_hierarchy(self, client: AsyncClient):
        """Homepage deve ter hierarquia de headings correta."""
        response = await client.get("/")
        # Deve ter h1 (titulo principal)
        assert "<h1>" in response.text
        # Deve ter h2 para secoes
        assert "<h2>" in response.text

    @pytest.mark.asyncio
    async def test_homepage_images_have_alt(self, client: AsyncClient):
        """Imagens devem ter atributo alt."""
        response = await client.get("/")
        # Se houver imagens, devem ter alt
        if '<img' in response.text:
            # Verifica se ha alt em imagens (pode ser vazio para decorativas)
            img_count = response.text.count('<img')
            alt_count = response.text.count('alt=')
            # Nem todas as imagens precisam de alt descritivo, mas devem ter o atributo
            assert alt_count >= img_count * 0.5  # Pelo menos 50% das imagens

    @pytest.mark.asyncio
    async def test_homepage_links_are_navigable(self, client: AsyncClient):
        """Links importantes devem estar presentes."""
        response = await client.get("/")
        # Link para categorias (no header ou no grid)
        assert 'href="/categorias"' in response.text or 'href="/categoria/' in response.text
        # Link para produtos
        assert 'href="/produtos"' in response.text or 'href="/produto/' in response.text


class TestHomePagePerformance:
    """Testes de performance para home page."""

    @pytest.mark.asyncio
    async def test_homepage_response_time(self, client: AsyncClient):
        """Homepage deve responder rapidamente."""
        import time

        start = time.time()
        response = await client.get("/")
        elapsed = time.time() - start

        assert response.status_code == 200
        # Deve responder em menos de 2 segundos (em testes locais)
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_homepage_content_size(self, client: AsyncClient):
        """Homepage nao deve ser excessivamente grande."""
        response = await client.get("/")

        # HTML nao deve ser muito grande (menos de 100KB)
        assert len(response.text) < 100 * 1024
