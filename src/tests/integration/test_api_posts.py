"""
Testes de integracao para endpoints de Posts.

Testa o fluxo completo HTTP -> API -> Banco de dados.
"""

import pytest


class TestPostEndpoints:
    """Testes para /api/v1/posts."""

    # -------------------------------------------------------------------------
    # POST /posts - Criar post
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_post_success(self, client, post_data):
        """Deve criar um novo post com dados validos."""
        # Act
        response = await client.post("/api/v1/posts", json=post_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == post_data["title"]
        assert data["slug"] == post_data["slug"]
        assert data["type"] == post_data["type"]
        assert data["status"] == "draft"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_post_duplicate_slug(self, client, post_data):
        """Deve retornar erro 400 ao criar post com slug duplicado."""
        # Arrange - Cria primeiro post
        await client.post("/api/v1/posts", json=post_data)

        # Act - Tenta criar segundo com mesmo slug
        post_data["title"] = "Outro titulo"
        response = await client.post("/api/v1/posts", json=post_data)

        # Assert
        assert response.status_code == 400
        assert "Slug ja existe" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_post_with_category(self, client, post_data):
        """Deve criar post vinculado a uma categoria."""
        # Arrange - Cria categoria
        category_response = await client.post(
            "/api/v1/categories",
            json={"name": "Funko Pop", "slug": "funko-pop"},
        )
        category_id = category_response.json()["id"]

        # Act - Cria post com categoria
        post_data["category_id"] = category_id
        response = await client.post("/api/v1/posts", json=post_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["category_id"] == category_id

    # -------------------------------------------------------------------------
    # GET /posts - Listar posts
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_posts_empty(self, client):
        """Deve retornar lista vazia quando nao ha posts."""
        # Act
        response = await client.get("/api/v1/posts")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_posts_with_pagination(self, client, post_data):
        """Deve retornar posts paginados."""
        # Arrange - Cria 5 posts
        for i in range(5):
            await client.post(
                "/api/v1/posts",
                json={**post_data, "slug": f"post-{i}", "title": f"Post {i}"},
            )

        # Act - Busca pagina 1 com 3 itens
        response = await client.get("/api/v1/posts?page=1&per_page=3")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5

    @pytest.mark.asyncio
    async def test_list_posts_filter_by_status(self, client, post_data):
        """Deve filtrar posts por status."""
        # Arrange - Cria post draft
        await client.post("/api/v1/posts", json=post_data)

        # Act - Filtra por draft
        response = await client.get("/api/v1/posts?status=draft")

        # Assert
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["status"] == "draft"

    # -------------------------------------------------------------------------
    # GET /posts/published - Posts publicados
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_published_posts_empty(self, client, post_data):
        """Deve retornar vazio se nao ha posts publicados."""
        # Arrange - Cria post em draft (nao publicado)
        await client.post("/api/v1/posts", json=post_data)

        # Act
        response = await client.get("/api/v1/posts/published")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_published_posts_only_published(self, client, post_data):
        """Deve retornar apenas posts publicados."""
        from datetime import datetime, timedelta, UTC

        # Arrange - Cria post e publica com publish_at no passado
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Publica o post com data de publicacao no passado
        publish_at = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published", "publish_at": publish_at},
        )

        # Act
        response = await client.get("/api/v1/posts/published")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "published"

    # -------------------------------------------------------------------------
    # GET /posts/{id} - Buscar por ID
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_post_by_id(self, client, post_data):
        """Deve retornar post por ID."""
        # Arrange - Cria post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Act
        response = await client.get(f"/api/v1/posts/{post_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == post_id
        assert data["title"] == post_data["title"]

    @pytest.mark.asyncio
    async def test_get_post_not_found(self, client):
        """Deve retornar 404 para ID inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/posts/{fake_id}")

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # GET /posts/slug/{slug} - Buscar por slug
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_post_by_slug(self, client, post_data):
        """Deve retornar post por slug."""
        # Arrange - Cria post
        await client.post("/api/v1/posts", json=post_data)

        # Act
        response = await client.get(f"/api/v1/posts/slug/{post_data['slug']}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == post_data["slug"]

    @pytest.mark.asyncio
    async def test_get_post_by_slug_not_found(self, client):
        """Deve retornar 404 para slug inexistente."""
        # Act
        response = await client.get("/api/v1/posts/slug/slug-inexistente")

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # PATCH /posts/{id} - Atualizar post
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_update_post(self, client, post_data):
        """Deve atualizar dados do post."""
        # Arrange - Cria post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Act - Atualiza titulo e conteudo
        response = await client.patch(
            f"/api/v1/posts/{post_id}",
            json={
                "title": "Titulo Atualizado",
                "content": "<p>Conteudo atualizado</p>",
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Titulo Atualizado"
        assert data["content"] == "<p>Conteudo atualizado</p>"
        assert data["slug"] == post_data["slug"]  # Inalterado

    @pytest.mark.asyncio
    async def test_update_post_not_found(self, client):
        """Deve retornar 404 ao atualizar post inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/api/v1/posts/{fake_id}",
            json={"title": "Novo Titulo"},
        )

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_post_slug_duplicate(self, client, post_data):
        """Deve retornar erro ao atualizar para slug ja existente."""
        # Arrange - Cria 2 posts
        await client.post("/api/v1/posts", json=post_data)
        create_response = await client.post(
            "/api/v1/posts",
            json={**post_data, "slug": "outro-slug", "title": "Outro post"},
        )
        post_id = create_response.json()["id"]

        # Act - Tenta atualizar slug para o do primeiro post
        response = await client.patch(
            f"/api/v1/posts/{post_id}",
            json={"slug": post_data["slug"]},
        )

        # Assert
        assert response.status_code == 400
        assert "Slug ja existe" in response.json()["detail"]

    # -------------------------------------------------------------------------
    # PATCH /posts/{id}/status - Atualizar status
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_update_post_status_to_published(self, client, post_data):
        """Deve publicar um post."""
        # Arrange - Cria post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Act - Publica
        response = await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"

    @pytest.mark.asyncio
    async def test_update_post_status_to_archived(self, client, post_data):
        """Deve arquivar um post."""
        # Arrange - Cria e publica post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "published"},
        )

        # Act - Arquiva
        response = await client.patch(
            f"/api/v1/posts/{post_id}/status",
            json={"status": "archived"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "archived"

    @pytest.mark.asyncio
    async def test_update_post_status_not_found(self, client):
        """Deve retornar 404 ao atualizar status de post inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/api/v1/posts/{fake_id}/status",
            json={"status": "published"},
        )

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # POST /posts/{id}/view - Incrementar views
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_increment_view(self, client, post_data):
        """Deve incrementar contador de views."""
        # Arrange - Cria post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Act - Incrementa view
        response = await client.post(f"/api/v1/posts/{post_id}/view")

        # Assert
        assert response.status_code == 200
        assert "registrada" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_increment_view_not_found(self, client):
        """Deve retornar 404 para post inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.post(f"/api/v1/posts/{fake_id}/view")

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # DELETE /posts/{id} - Remover post
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_delete_post(self, client, post_data):
        """Deve remover post existente."""
        # Arrange - Cria post
        create_response = await client.post("/api/v1/posts", json=post_data)
        post_id = create_response.json()["id"]

        # Act
        response = await client.delete(f"/api/v1/posts/{post_id}")

        # Assert
        assert response.status_code == 200
        assert "sucesso" in response.json()["message"].lower()

        # Verifica que nao existe mais
        get_response = await client.get(f"/api/v1/posts/{post_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_post_not_found(self, client):
        """Deve retornar 404 ao deletar post inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/posts/{fake_id}")

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # Testes de tipos de post
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_post_product_single(self, client, post_data):
        """Deve criar post do tipo product_single."""
        # Act
        post_data["type"] = "product_single"
        post_data["slug"] = "produto-individual"
        response = await client.post("/api/v1/posts", json=post_data)

        # Assert
        assert response.status_code == 201
        assert response.json()["type"] == "product_single"

    @pytest.mark.asyncio
    async def test_create_post_guide(self, client, post_data):
        """Deve criar post do tipo guide."""
        # Act
        post_data["type"] = "guide"
        post_data["slug"] = "guia-completo"
        response = await client.post("/api/v1/posts", json=post_data)

        # Assert
        assert response.status_code == 201
        assert response.json()["type"] == "guide"

    @pytest.mark.asyncio
    async def test_create_post_invalid_type(self, client, post_data):
        """Deve retornar erro para tipo invalido."""
        # Act
        post_data["type"] = "tipo_invalido"
        response = await client.post("/api/v1/posts", json=post_data)

        # Assert
        assert response.status_code == 422
