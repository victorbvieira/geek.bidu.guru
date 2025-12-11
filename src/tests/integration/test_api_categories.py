"""
Testes de integração para endpoints de Categories.

Testa o fluxo completo HTTP -> API -> Banco de dados.
"""

import pytest


class TestCategoryEndpoints:
    """Testes para /api/v1/categories."""

    # -------------------------------------------------------------------------
    # POST /categories - Criar categoria
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_category_success(self, client):
        """Deve criar uma nova categoria com dados válidos."""
        # Arrange
        payload = {
            "name": "Star Wars",
            "slug": "star-wars",
            "description": "Produtos do universo Star Wars",
        }

        # Act
        response = await client.post("/api/v1/categories", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Star Wars"
        assert data["slug"] == "star-wars"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_category_duplicate_slug(self, client):
        """Deve retornar erro 400 ao criar categoria com slug duplicado."""
        # Arrange - Cria primeira categoria
        payload = {
            "name": "Categoria 1",
            "slug": "slug-duplicado",
            "description": "Primeira categoria",
        }
        await client.post("/api/v1/categories", json=payload)

        # Act - Tenta criar segunda com mesmo slug
        payload["name"] = "Categoria 2"
        response = await client.post("/api/v1/categories", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Slug ja existe" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_category_with_parent(self, client):
        """Deve criar categoria filha com parent_id válido."""
        # Arrange - Cria categoria pai
        parent_response = await client.post(
            "/api/v1/categories",
            json={
                "name": "Categoria Pai",
                "slug": "categoria-pai",
            },
        )
        parent_id = parent_response.json()["id"]

        # Act - Cria categoria filha
        response = await client.post(
            "/api/v1/categories",
            json={
                "name": "Categoria Filha",
                "slug": "categoria-filha",
                "parent_id": parent_id,
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == parent_id

    # -------------------------------------------------------------------------
    # GET /categories - Listar categorias
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_categories_empty(self, client):
        """Deve retornar lista vazia quando não há categorias."""
        # Act
        response = await client.get("/api/v1/categories")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_categories_with_pagination(self, client):
        """Deve retornar categorias paginadas."""
        # Arrange - Cria 5 categorias
        for i in range(5):
            await client.post(
                "/api/v1/categories",
                json={
                    "name": f"Categoria {i}",
                    "slug": f"categoria-{i}",
                },
            )

        # Act - Busca página 1 com 3 itens
        response = await client.get("/api/v1/categories?page=1&per_page=3")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5

    # -------------------------------------------------------------------------
    # GET /categories/root - Categorias raiz
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_root_categories(self, client):
        """Deve retornar apenas categorias sem parent."""
        # Arrange - Cria categoria pai e filha
        parent_response = await client.post(
            "/api/v1/categories",
            json={"name": "Pai", "slug": "pai"},
        )
        parent_id = parent_response.json()["id"]

        await client.post(
            "/api/v1/categories",
            json={"name": "Filha", "slug": "filha", "parent_id": parent_id},
        )

        # Act
        response = await client.get("/api/v1/categories/root")

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Apenas a categoria raiz deve aparecer
        assert len(data) == 1
        assert data[0]["name"] == "Pai"

    # -------------------------------------------------------------------------
    # GET /categories/{id} - Buscar por ID
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_category_by_id(self, client):
        """Deve retornar categoria por ID."""
        # Arrange - Cria categoria
        create_response = await client.post(
            "/api/v1/categories",
            json={
                "name": "Marvel",
                "slug": "marvel",
                "description": "Produtos Marvel",
            },
        )
        category_id = create_response.json()["id"]

        # Act
        response = await client.get(f"/api/v1/categories/{category_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Marvel"

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, client):
        """Deve retornar 404 para ID inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/categories/{fake_id}")

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # GET /categories/slug/{slug} - Buscar por slug
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_category_by_slug(self, client):
        """Deve retornar categoria por slug."""
        # Arrange - Cria categoria
        await client.post(
            "/api/v1/categories",
            json={
                "name": "DC Comics",
                "slug": "dc-comics",
            },
        )

        # Act
        response = await client.get("/api/v1/categories/slug/dc-comics")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "dc-comics"
        assert data["name"] == "DC Comics"

    @pytest.mark.asyncio
    async def test_get_category_by_slug_not_found(self, client):
        """Deve retornar 404 para slug inexistente."""
        # Act
        response = await client.get("/api/v1/categories/slug/inexistente")

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # GET /categories/{id}/children - Filhas de uma categoria
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_category_children(self, client):
        """Deve retornar categorias filhas."""
        # Arrange - Cria hierarquia
        parent_response = await client.post(
            "/api/v1/categories",
            json={"name": "Games", "slug": "games"},
        )
        parent_id = parent_response.json()["id"]

        for i in range(3):
            await client.post(
                "/api/v1/categories",
                json={
                    "name": f"Sub-Games {i}",
                    "slug": f"sub-games-{i}",
                    "parent_id": parent_id,
                },
            )

        # Act
        response = await client.get(f"/api/v1/categories/{parent_id}/children")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    # -------------------------------------------------------------------------
    # PATCH /categories/{id} - Atualizar categoria
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_update_category(self, client):
        """Deve atualizar dados da categoria."""
        # Arrange - Cria categoria
        create_response = await client.post(
            "/api/v1/categories",
            json={
                "name": "Nome Original",
                "slug": "nome-original",
            },
        )
        category_id = create_response.json()["id"]

        # Act - Atualiza nome e descrição
        response = await client.patch(
            f"/api/v1/categories/{category_id}",
            json={
                "name": "Nome Atualizado",
                "description": "Nova descrição",
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nome Atualizado"
        assert data["description"] == "Nova descrição"
        assert data["slug"] == "nome-original"  # Inalterado

    # -------------------------------------------------------------------------
    # DELETE /categories/{id} - Remover categoria
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_delete_category(self, client):
        """Deve remover categoria existente."""
        # Arrange - Cria categoria
        create_response = await client.post(
            "/api/v1/categories",
            json={
                "name": "Para Deletar",
                "slug": "para-deletar",
            },
        )
        category_id = create_response.json()["id"]

        # Act
        response = await client.delete(f"/api/v1/categories/{category_id}")

        # Assert
        assert response.status_code == 200
        assert "sucesso" in response.json()["message"].lower()

        # Verifica que não existe mais
        get_response = await client.get(f"/api/v1/categories/{category_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, client):
        """Deve retornar 404 ao deletar categoria inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/categories/{fake_id}")

        # Assert
        assert response.status_code == 404
