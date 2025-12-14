"""
Testes de integracao para rotas SSR (Server-Side Rendering).

Testa as paginas publicas do blog.
"""

import pytest


class TestSSRRoutes:
    """Testes para rotas SSR do blog."""

    # -------------------------------------------------------------------------
    # Homepage
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_homepage(self, client):
        """Homepage deve carregar com sucesso."""
        response = await client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "geek.bidu.guru" in response.text

    # -------------------------------------------------------------------------
    # Blog
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_blog_list_empty(self, client):
        """Listagem de blog deve funcionar mesmo sem posts."""
        response = await client.get("/blog")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Blog" in response.text

    @pytest.mark.asyncio
    async def test_blog_list_with_posts(self, client, post_data):
        """Listagem de blog deve exibir posts publicados."""
        from datetime import datetime, timedelta, UTC

        # Arrange - Cria post e publica
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Publica com data no passado
        publish_at = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published", "publish_at": publish_at},
        )

        # Act
        response = await client.get("/blog")

        # Assert
        assert response.status_code == 200
        assert post_data["title"] in response.text

    @pytest.mark.asyncio
    async def test_blog_pagination(self, client):
        """Paginacao deve funcionar."""
        response = await client.get("/blog?page=1&per_page=10")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    # -------------------------------------------------------------------------
    # Post Individual
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_post_not_found(self, client):
        """Post inexistente deve retornar 404."""
        response = await client.get("/blog/slug-que-nao-existe")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_post_draft_not_accessible(self, client, post_data):
        """Post em draft nao deve ser acessivel publicamente."""
        # Arrange - Cria post (fica em draft por padrao)
        await client.post("/api/v1/posts", json=post_data)

        # Act - Tenta acessar post em draft
        response = await client.get(f"/blog/{post_data['slug']}")

        # Assert - Deve retornar 404 (nao publicado)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_post_published_accessible(self, client, post_data):
        """Post publicado deve ser acessivel."""
        from datetime import datetime, timedelta, UTC

        # Arrange - Cria post e publica
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Publica com data no passado
        publish_at = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published", "publish_at": publish_at},
        )

        # Act
        response = await client.get(f"/blog/{post_data['slug']}")

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert post_data["title"] in response.text

    # -------------------------------------------------------------------------
    # Categorias
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_categories_list(self, client):
        """Listagem de categorias deve funcionar."""
        response = await client.get("/categorias")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Categorias" in response.text

    @pytest.mark.asyncio
    async def test_category_not_found(self, client):
        """Categoria inexistente deve retornar 404."""
        response = await client.get("/categoria/categoria-que-nao-existe")

        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.postgresql
    async def test_category_page(self, client, category_data):
        """Pagina de categoria deve funcionar. Requer PostgreSQL (JSONB)."""
        # Arrange - Cria categoria
        await client.post("/api/v1/categories", json=category_data)

        # Act
        response = await client.get(f"/categoria/{category_data['slug']}")

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert category_data["name"] in response.text

    @pytest.mark.asyncio
    @pytest.mark.postgresql
    async def test_category_with_posts(self, client, category_data, post_data):
        """Categoria deve exibir posts vinculados. Requer PostgreSQL (JSONB)."""
        from datetime import datetime, timedelta, UTC

        # Arrange - Cria categoria
        cat_response = await client.post("/api/v1/categories", json=category_data)
        category_id = cat_response.json()["id"]

        # Cria post vinculado a categoria
        post_data["category_id"] = category_id
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Publica post
        publish_at = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published", "publish_at": publish_at},
        )

        # Act
        response = await client.get(f"/categoria/{category_data['slug']}")

        # Assert
        assert response.status_code == 200
        assert post_data["title"] in response.text

    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Health check deve retornar status."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
