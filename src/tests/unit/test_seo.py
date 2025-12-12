"""
Testes para funcionalidades SEO.

Verifica:
- Canonical URLs em todas as paginas
- Schema.org JSON-LD (Organization, WebSite, BreadcrumbList, BlogPosting)
- Meta robots (index/noindex)
- Open Graph meta tags
- Twitter Cards
"""

import pytest
from httpx import AsyncClient


class TestCanonicalURLs:
    """Testes para canonical URLs."""

    @pytest.mark.asyncio
    async def test_homepage_has_canonical(self, client: AsyncClient):
        """Homepage deve ter canonical URL."""
        response = await client.get("/")

        assert response.status_code == 200
        assert 'rel="canonical"' in response.text

    @pytest.mark.asyncio
    async def test_blog_list_has_canonical(self, client: AsyncClient):
        """Lista de posts deve ter canonical URL."""
        response = await client.get("/blog")

        assert response.status_code == 200
        assert 'rel="canonical"' in response.text
        assert "/blog" in response.text

    @pytest.mark.asyncio
    async def test_blog_list_page2_has_canonical_with_page(self, client: AsyncClient):
        """Pagina 2 do blog deve ter canonical com ?page=2."""
        response = await client.get("/blog?page=2")

        assert response.status_code == 200
        assert 'rel="canonical"' in response.text
        # Canonical deve incluir page=2
        assert "page=2" in response.text

    @pytest.mark.asyncio
    async def test_categories_page_has_canonical(self, client: AsyncClient):
        """Pagina de categorias deve ter canonical URL."""
        response = await client.get("/categorias")

        assert response.status_code == 200
        assert 'rel="canonical"' in response.text
        assert "/categorias" in response.text

    @pytest.mark.asyncio
    async def test_search_page_has_canonical(self, client: AsyncClient):
        """Pagina de busca deve ter canonical URL."""
        response = await client.get("/busca")

        assert response.status_code == 200
        assert 'rel="canonical"' in response.text


class TestMetaRobots:
    """Testes para meta robots."""

    @pytest.mark.asyncio
    async def test_homepage_is_indexable(self, client: AsyncClient):
        """Homepage deve ser indexavel."""
        response = await client.get("/")

        assert response.status_code == 200
        # Deve ter index, follow (ou nao ter noindex)
        assert "noindex" not in response.text.lower() or 'content="index' in response.text.lower()

    @pytest.mark.asyncio
    async def test_blog_list_is_indexable(self, client: AsyncClient):
        """Lista de posts deve ser indexavel."""
        response = await client.get("/blog")

        assert response.status_code == 200
        # Nao deve ter noindex
        text_lower = response.text.lower()
        # Verifica se tem robots com index ou nao tem noindex
        has_noindex = 'name="robots"' in text_lower and "noindex" in text_lower
        assert not has_noindex or 'content="index' in text_lower

    @pytest.mark.asyncio
    async def test_search_page_is_noindex(self, client: AsyncClient):
        """Pagina de busca deve ser noindex."""
        response = await client.get("/busca")

        assert response.status_code == 200
        assert "noindex" in response.text.lower()

    @pytest.mark.asyncio
    async def test_search_with_query_is_noindex(self, client: AsyncClient):
        """Pagina de busca com query deve ser noindex."""
        response = await client.get("/busca?q=teste")

        assert response.status_code == 200
        assert "noindex" in response.text.lower()


class TestSchemaOrg:
    """Testes para Schema.org JSON-LD."""

    @pytest.mark.asyncio
    async def test_homepage_has_organization_schema(self, client: AsyncClient):
        """Homepage deve ter Schema Organization."""
        response = await client.get("/")

        assert response.status_code == 200
        assert '"@type": "Organization"' in response.text or '"@type":"Organization"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_website_schema(self, client: AsyncClient):
        """Homepage deve ter Schema WebSite."""
        response = await client.get("/")

        assert response.status_code == 200
        assert '"@type": "WebSite"' in response.text or '"@type":"WebSite"' in response.text

    @pytest.mark.asyncio
    async def test_website_schema_has_search_action(self, client: AsyncClient):
        """Schema WebSite deve ter SearchAction."""
        response = await client.get("/")

        assert response.status_code == 200
        assert "SearchAction" in response.text

    @pytest.mark.asyncio
    async def test_blog_list_has_breadcrumb_schema(self, client: AsyncClient):
        """Lista de posts deve ter Schema BreadcrumbList."""
        response = await client.get("/blog")

        assert response.status_code == 200
        assert "BreadcrumbList" in response.text

    @pytest.mark.asyncio
    async def test_categories_page_has_breadcrumb_schema(self, client: AsyncClient):
        """Pagina de categorias deve ter Schema BreadcrumbList."""
        response = await client.get("/categorias")

        assert response.status_code == 200
        assert "BreadcrumbList" in response.text


class TestOpenGraph:
    """Testes para Open Graph meta tags."""

    @pytest.mark.asyncio
    async def test_homepage_has_og_title(self, client: AsyncClient):
        """Homepage deve ter og:title."""
        response = await client.get("/")

        assert response.status_code == 200
        assert 'property="og:title"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_og_description(self, client: AsyncClient):
        """Homepage deve ter og:description."""
        response = await client.get("/")

        assert response.status_code == 200
        assert 'property="og:description"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_og_type(self, client: AsyncClient):
        """Homepage deve ter og:type."""
        response = await client.get("/")

        assert response.status_code == 200
        assert 'property="og:type"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_og_url(self, client: AsyncClient):
        """Homepage deve ter og:url."""
        response = await client.get("/")

        assert response.status_code == 200
        assert 'property="og:url"' in response.text

    @pytest.mark.asyncio
    async def test_blog_list_has_og_tags(self, client: AsyncClient):
        """Lista de posts deve ter tags OG."""
        response = await client.get("/blog")

        assert response.status_code == 200
        assert 'property="og:title"' in response.text
        assert 'property="og:description"' in response.text


class TestTwitterCards:
    """Testes para Twitter Cards."""

    @pytest.mark.asyncio
    async def test_homepage_has_twitter_card(self, client: AsyncClient):
        """Homepage deve ter twitter:card."""
        response = await client.get("/")

        assert response.status_code == 200
        assert 'name="twitter:card"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_twitter_title(self, client: AsyncClient):
        """Homepage deve ter twitter:title."""
        response = await client.get("/")

        assert response.status_code == 200
        assert 'name="twitter:title"' in response.text

    @pytest.mark.asyncio
    async def test_homepage_has_twitter_description(self, client: AsyncClient):
        """Homepage deve ter twitter:description."""
        response = await client.get("/")

        assert response.status_code == 200
        assert 'name="twitter:description"' in response.text


class TestSEOIntegration:
    """Testes de integracao SEO."""

    @pytest.mark.asyncio
    async def test_all_pages_have_basic_seo(self, client: AsyncClient):
        """Todas as paginas publicas devem ter SEO basico."""
        pages = ["/", "/blog", "/categorias", "/busca"]

        for page in pages:
            response = await client.get(page)
            assert response.status_code == 200, f"Pagina {page} retornou {response.status_code}"

            # Deve ter canonical
            assert 'rel="canonical"' in response.text, f"Pagina {page} sem canonical"

            # Deve ter OG tags
            assert 'property="og:title"' in response.text, f"Pagina {page} sem og:title"

            # Deve ter Twitter card
            assert 'name="twitter:card"' in response.text, f"Pagina {page} sem twitter:card"

    @pytest.mark.asyncio
    async def test_schema_org_is_valid_json(self, client: AsyncClient):
        """Schema.org deve ser JSON valido."""
        import json
        import re

        response = await client.get("/")
        assert response.status_code == 200

        # Encontra todos os blocos JSON-LD
        pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(pattern, response.text, re.DOTALL)

        assert len(matches) > 0, "Nenhum Schema.org encontrado"

        for match in matches:
            try:
                data = json.loads(match.strip())
                assert "@context" in data, "Schema sem @context"
                assert "@type" in data, "Schema sem @type"
            except json.JSONDecodeError as e:
                pytest.fail(f"JSON-LD invalido: {e}")
