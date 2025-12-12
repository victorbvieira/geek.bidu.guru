"""
Testes de integracao para paginas de erro.

Testa os exception handlers para 404 e 500.
"""

import pytest


class TestErrorPages:
    """Testes para paginas de erro."""

    # -------------------------------------------------------------------------
    # 404 Not Found
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_404_html_page(self, client):
        """Pagina 404 deve retornar HTML para requests SSR."""
        response = await client.get(
            "/pagina-que-nao-existe",
            headers={"Accept": "text/html"},
        )

        assert response.status_code == 404
        assert "text/html" in response.headers["content-type"]
        assert "404" in response.text
        assert "Pagina nao encontrada" in response.text

    @pytest.mark.asyncio
    async def test_404_json_api(self, client):
        """API 404 deve retornar JSON."""
        # Usa UUID valido mas inexistente
        response = await client.get(
            "/api/v1/posts/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_404_blog_post_not_found(self, client):
        """Post inexistente deve mostrar pagina 404."""
        response = await client.get(
            "/blog/post-que-nao-existe",
            headers={"Accept": "text/html"},
        )

        assert response.status_code == 404
        assert "404" in response.text

    @pytest.mark.asyncio
    async def test_404_category_not_found(self, client):
        """Categoria inexistente deve mostrar pagina 404."""
        response = await client.get(
            "/categoria/categoria-que-nao-existe",
            headers={"Accept": "text/html"},
        )

        assert response.status_code == 404
        assert "404" in response.text

    @pytest.mark.asyncio
    async def test_404_goto_not_found(self, client):
        """Produto inexistente em /goto deve retornar 404."""
        response = await client.get("/goto/produto-que-nao-existe")

        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # 404 com sugestoes
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_404_has_navigation_links(self, client):
        """Pagina 404 deve ter links de navegacao."""
        response = await client.get(
            "/pagina-inexistente",
            headers={"Accept": "text/html"},
        )

        assert response.status_code == 404
        assert "Voltar para Home" in response.text
        assert "Ver Blog" in response.text

    # -------------------------------------------------------------------------
    # API vs SSR detection
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_api_path_returns_json(self, client):
        """Paths /api/* devem retornar JSON mesmo sem header Accept."""
        response = await client.get("/api/v1/nonexistent")

        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_accept_json_returns_json(self, client):
        """Request com Accept: application/json deve retornar JSON."""
        response = await client.get(
            "/pagina-inexistente",
            headers={"Accept": "application/json"},
        )

        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]

    # -------------------------------------------------------------------------
    # Health check sempre JSON
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_health_always_json(self, client):
        """Health check deve sempre retornar JSON."""
        response = await client.get(
            "/health",
            headers={"Accept": "text/html"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
