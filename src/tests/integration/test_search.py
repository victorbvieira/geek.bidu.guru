"""
Testes de integracao para busca.

Testa o endpoint /busca.
"""

import pytest


class TestSearch:
    """Testes para pagina de busca."""

    # -------------------------------------------------------------------------
    # Pagina de busca
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_page_loads(self, client):
        """Pagina de busca deve carregar sem query."""
        response = await client.get("/busca")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Busca" in response.text

    @pytest.mark.asyncio
    async def test_search_with_empty_query(self, client):
        """Busca com query vazia deve mostrar sugestoes."""
        response = await client.get("/busca?q=")

        assert response.status_code == 200
        assert "Sugestoes de busca" in response.text

    @pytest.mark.asyncio
    async def test_search_no_results(self, client):
        """Busca sem resultados deve mostrar mensagem."""
        response = await client.get("/busca?q=xyzabc123naoexiste")

        assert response.status_code == 200
        assert "Nenhum resultado" in response.text

    @pytest.mark.asyncio
    async def test_search_with_results(self, client, post_data):
        """Busca deve encontrar posts publicados."""
        from datetime import datetime, timedelta, UTC

        # Arrange - Cria e publica post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Publica com data no passado
        publish_at = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published", "publish_at": publish_at},
        )

        # Act - Busca por termo no titulo
        response = await client.get("/busca?q=Produtos+Geek")

        # Assert
        assert response.status_code == 200
        assert post_data["title"] in response.text

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, client, post_data):
        """Busca deve ser case insensitive."""
        from datetime import datetime, timedelta, UTC

        # Arrange - Cria e publica post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        publish_at = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published", "publish_at": publish_at},
        )

        # Act - Busca em minusculas
        response = await client.get("/busca?q=produtos+geek")

        # Assert
        assert response.status_code == 200
        assert post_data["title"] in response.text

    @pytest.mark.asyncio
    async def test_search_draft_not_found(self, client, post_data):
        """Busca nao deve encontrar posts em draft."""
        # Arrange - Cria post (fica em draft por padrao)
        await client.post("/api/v1/posts", json=post_data)

        # Act - Busca por termo no titulo
        response = await client.get("/busca?q=Produtos+Geek")

        # Assert - Nao deve encontrar (post em draft)
        assert response.status_code == 200
        assert "Nenhum resultado" in response.text

    # -------------------------------------------------------------------------
    # Paginacao
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_pagination_params(self, client):
        """Busca deve aceitar parametros de paginacao."""
        response = await client.get("/busca?q=teste&page=1&per_page=10")

        assert response.status_code == 200

    # -------------------------------------------------------------------------
    # Caracteres especiais
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_special_characters(self, client):
        """Busca deve lidar com caracteres especiais."""
        response = await client.get("/busca?q=star+wars")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_url_encoded(self, client):
        """Busca deve lidar com URL encoding."""
        response = await client.get("/busca?q=presen%C3%A7a")  # presença

        assert response.status_code == 200
