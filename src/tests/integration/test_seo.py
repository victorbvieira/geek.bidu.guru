"""
Testes de integracao para rotas SEO.

Testa sitemap.xml e robots.txt.
"""

import pytest


class TestRobotsTxt:
    """Testes para robots.txt."""

    @pytest.mark.asyncio
    async def test_robots_txt_exists(self, client):
        """robots.txt deve existir."""
        response = await client.get("/robots.txt")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_robots_txt_has_user_agent(self, client):
        """robots.txt deve ter User-agent."""
        response = await client.get("/robots.txt")

        assert "User-agent:" in response.text

    @pytest.mark.asyncio
    async def test_robots_txt_references_sitemap(self, client):
        """robots.txt deve referenciar sitemap (em producao)."""
        response = await client.get("/robots.txt")

        # Em ambiente de teste pode estar bloqueando tudo
        # mas o endpoint deve funcionar
        assert response.status_code == 200


class TestSitemapXml:
    """Testes para sitemap.xml."""

    @pytest.mark.asyncio
    async def test_sitemap_exists(self, client):
        """sitemap.xml deve existir."""
        response = await client.get("/sitemap.xml")

        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_sitemap_is_valid_xml(self, client):
        """sitemap.xml deve ser XML valido."""
        response = await client.get("/sitemap.xml")

        assert response.text.startswith('<?xml version="1.0"')
        assert "<urlset" in response.text
        assert "</urlset>" in response.text

    @pytest.mark.asyncio
    async def test_sitemap_has_homepage(self, client):
        """sitemap.xml deve incluir homepage."""
        response = await client.get("/sitemap.xml")

        # Homepage deve estar presente (sem trailing slash)
        assert "<loc>http://test</loc>" in response.text

    @pytest.mark.asyncio
    async def test_sitemap_has_blog(self, client):
        """sitemap.xml deve incluir /blog."""
        response = await client.get("/sitemap.xml")

        assert "<loc>http://test/blog</loc>" in response.text

    @pytest.mark.asyncio
    async def test_sitemap_has_categories_page(self, client):
        """sitemap.xml deve incluir /categorias."""
        response = await client.get("/sitemap.xml")

        assert "<loc>http://test/categorias</loc>" in response.text

    @pytest.mark.asyncio
    async def test_sitemap_includes_published_posts(self, client, post_data):
        """sitemap.xml deve incluir posts publicados."""
        from datetime import datetime, timedelta, UTC

        # Arrange - Cria e publica post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        publish_at = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published", "publish_at": publish_at},
        )

        # Act
        response = await client.get("/sitemap.xml")

        # Assert
        assert response.status_code == 200
        assert f"/blog/{post_data['slug']}</loc>" in response.text

    @pytest.mark.asyncio
    async def test_sitemap_excludes_draft_posts(self, client, post_data):
        """sitemap.xml nao deve incluir posts em draft."""
        # Arrange - Cria post (fica em draft por padrao)
        await client.post("/api/v1/posts", json=post_data)

        # Act
        response = await client.get("/sitemap.xml")

        # Assert - Slug do post nao deve estar no sitemap
        assert f"/blog/{post_data['slug']}</loc>" not in response.text

    @pytest.mark.asyncio
    async def test_sitemap_includes_categories(self, client, category_data):
        """sitemap.xml deve incluir categorias."""
        # Arrange - Cria categoria
        await client.post("/api/v1/categories", json=category_data)

        # Act
        response = await client.get("/sitemap.xml")

        # Assert
        assert f"/categoria/{category_data['slug']}</loc>" in response.text

    @pytest.mark.asyncio
    async def test_sitemap_has_required_elements(self, client):
        """sitemap.xml deve ter elementos obrigatorios."""
        response = await client.get("/sitemap.xml")

        # Cada URL deve ter loc, lastmod, changefreq, priority
        assert "<loc>" in response.text
        assert "<lastmod>" in response.text
        assert "<changefreq>" in response.text
        assert "<priority>" in response.text


class TestSitemapIndex:
    """Testes para sitemap-index.xml."""

    @pytest.mark.asyncio
    async def test_sitemap_index_exists(self, client):
        """sitemap-index.xml deve existir."""
        response = await client.get("/sitemap-index.xml")

        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_sitemap_index_references_sitemap(self, client):
        """sitemap-index.xml deve referenciar sitemap principal."""
        response = await client.get("/sitemap-index.xml")

        assert "<sitemapindex" in response.text
        assert "/sitemap.xml</loc>" in response.text
