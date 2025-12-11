"""
Testes de integração para endpoints de Products.

Testa o fluxo completo HTTP -> API -> Banco de dados.
"""

import pytest


class TestProductEndpoints:
    """Testes para /api/v1/products."""

    # -------------------------------------------------------------------------
    # POST /products - Criar produto
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_product_success(self, client):
        """Deve criar um novo produto com dados válidos."""
        # Arrange
        payload = {
            "name": "Funko Pop Darth Vader",
            "slug": "funko-pop-darth-vader",
            "short_description": "Boneco colecionável",
            "price": 149.90,
            "affiliate_url_raw": "https://amazon.com.br/dp/B123456?tag=geekbidu-20",
            "affiliate_redirect_slug": "funko-vader-amazon",
            "platform": "amazon",
            "availability": "available",
        }

        # Act
        response = await client.post("/api/v1/products", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Funko Pop Darth Vader"
        assert data["slug"] == "funko-pop-darth-vader"
        assert data["platform"] == "amazon"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_product_duplicate_slug(self, client):
        """Deve retornar erro 400 ao criar produto com slug duplicado."""
        # Arrange - Cria primeiro produto
        payload = {
            "name": "Produto 1",
            "slug": "slug-duplicado",
            "affiliate_url_raw": "https://amazon.com.br/dp/A123",
            "affiliate_redirect_slug": "redirect-1",
            "platform": "amazon",
        }
        await client.post("/api/v1/products", json=payload)

        # Act - Tenta criar segundo com mesmo slug
        payload["name"] = "Produto 2"
        payload["affiliate_redirect_slug"] = "redirect-2"
        response = await client.post("/api/v1/products", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Slug ja existe" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_product_duplicate_redirect_slug(self, client):
        """Deve retornar erro 400 ao criar produto com redirect_slug duplicado."""
        # Arrange - Cria primeiro produto
        payload = {
            "name": "Produto 1",
            "slug": "produto-1",
            "affiliate_url_raw": "https://amazon.com.br/dp/A123",
            "affiliate_redirect_slug": "redirect-duplicado",
            "platform": "amazon",
        }
        await client.post("/api/v1/products", json=payload)

        # Act - Tenta criar segundo com mesmo redirect_slug
        payload["name"] = "Produto 2"
        payload["slug"] = "produto-2"
        response = await client.post("/api/v1/products", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Redirect slug ja existe" in response.json()["detail"]

    # -------------------------------------------------------------------------
    # GET /products - Listar produtos
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_products_empty(self, client):
        """Deve retornar lista vazia quando não há produtos."""
        # Act
        response = await client.get("/api/v1/products")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_products_with_pagination(self, client):
        """Deve retornar produtos paginados."""
        # Arrange - Cria 5 produtos
        for i in range(5):
            await client.post(
                "/api/v1/products",
                json={
                    "name": f"Produto {i}",
                    "slug": f"produto-{i}",
                    "affiliate_url_raw": f"https://amazon.com.br/dp/A{i}",
                    "affiliate_redirect_slug": f"redirect-{i}",
                    "platform": "amazon",
                },
            )

        # Act - Busca página 1 com 3 itens
        response = await client.get("/api/v1/products?page=1&per_page=3")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5

    @pytest.mark.asyncio
    async def test_list_products_filter_by_platform(self, client):
        """Deve filtrar produtos por plataforma."""
        # Arrange - Cria produtos de diferentes plataformas
        await client.post(
            "/api/v1/products",
            json={
                "name": "Produto Amazon",
                "slug": "produto-amazon",
                "affiliate_url_raw": "https://amazon.com.br/dp/A1",
                "affiliate_redirect_slug": "amazon-1",
                "platform": "amazon",
            },
        )
        await client.post(
            "/api/v1/products",
            json={
                "name": "Produto ML",
                "slug": "produto-ml",
                "affiliate_url_raw": "https://mercadolivre.com.br/p/1",
                "affiliate_redirect_slug": "ml-1",
                "platform": "mercadolivre",
            },
        )

        # Act - Filtra apenas Amazon
        response = await client.get("/api/v1/products?platform=amazon")

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verifica que todos os produtos retornados são da Amazon
        for item in data["items"]:
            assert item["platform"] == "amazon"

    # -------------------------------------------------------------------------
    # GET /products/available - Produtos disponíveis
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_available_products(self, client):
        """Deve retornar apenas produtos disponíveis."""
        # Arrange - Cria produto disponível e indisponível
        await client.post(
            "/api/v1/products",
            json={
                "name": "Disponível",
                "slug": "disponivel",
                "affiliate_url_raw": "https://amazon.com.br/dp/A1",
                "affiliate_redirect_slug": "disp-1",
                "platform": "amazon",
                "availability": "available",
            },
        )
        await client.post(
            "/api/v1/products",
            json={
                "name": "Indisponível",
                "slug": "indisponivel",
                "affiliate_url_raw": "https://amazon.com.br/dp/A2",
                "affiliate_redirect_slug": "indisp-1",
                "platform": "amazon",
                "availability": "unavailable",
            },
        )

        # Act
        response = await client.get("/api/v1/products/available")

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Todos devem ser available
        for item in data["items"]:
            assert item["availability"] == "available"

    # -------------------------------------------------------------------------
    # GET /products/top-clicked - Mais clicados
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_top_clicked_products(self, client):
        """Deve retornar produtos ordenados por cliques."""
        # Arrange - Cria produtos (click_count é gerenciado internamente)
        for i in range(3):
            await client.post(
                "/api/v1/products",
                json={
                    "name": f"Produto {i}",
                    "slug": f"top-clicked-{i}",
                    "affiliate_url_raw": f"https://amazon.com.br/dp/TC{i}",
                    "affiliate_redirect_slug": f"tc-{i}",
                    "platform": "amazon",
                },
            )

        # Act
        response = await client.get("/api/v1/products/top-clicked?limit=5")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    # -------------------------------------------------------------------------
    # GET /products/{id} - Buscar por ID
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_product_by_id(self, client):
        """Deve retornar produto por ID."""
        # Arrange - Cria produto
        create_response = await client.post(
            "/api/v1/products",
            json={
                "name": "Produto Teste",
                "slug": "produto-teste",
                "affiliate_url_raw": "https://amazon.com.br/dp/TEST",
                "affiliate_redirect_slug": "test-1",
                "platform": "amazon",
            },
        )
        product_id = create_response.json()["id"]

        # Act
        response = await client.get(f"/api/v1/products/{product_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Produto Teste"

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, client):
        """Deve retornar 404 para ID inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/products/{fake_id}")

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # GET /products/slug/{slug} - Buscar por slug
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_product_by_slug(self, client):
        """Deve retornar produto por slug."""
        # Arrange - Cria produto
        await client.post(
            "/api/v1/products",
            json={
                "name": "Produto Slug",
                "slug": "produto-por-slug",
                "affiliate_url_raw": "https://amazon.com.br/dp/SLUG",
                "affiliate_redirect_slug": "slug-1",
                "platform": "amazon",
            },
        )

        # Act
        response = await client.get("/api/v1/products/slug/produto-por-slug")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "produto-por-slug"

    # -------------------------------------------------------------------------
    # PATCH /products/{id} - Atualizar produto
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_update_product(self, client):
        """Deve atualizar dados do produto."""
        # Arrange - Cria produto
        create_response = await client.post(
            "/api/v1/products",
            json={
                "name": "Nome Original",
                "slug": "nome-original-prod",
                "affiliate_url_raw": "https://amazon.com.br/dp/ORIG",
                "affiliate_redirect_slug": "orig-1",
                "platform": "amazon",
                "price": 100.00,
            },
        )
        product_id = create_response.json()["id"]

        # Act - Atualiza nome e preço
        response = await client.patch(
            f"/api/v1/products/{product_id}",
            json={
                "name": "Nome Atualizado",
                "price": 150.00,
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nome Atualizado"
        assert float(data["price"]) == 150.00

    # -------------------------------------------------------------------------
    # PATCH /products/{id}/price - Atualizar preço
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_update_product_price(self, client):
        """Deve atualizar apenas preço do produto."""
        # Arrange - Cria produto
        create_response = await client.post(
            "/api/v1/products",
            json={
                "name": "Produto Preço",
                "slug": "produto-preco",
                "affiliate_url_raw": "https://amazon.com.br/dp/PRECO",
                "affiliate_redirect_slug": "preco-1",
                "platform": "amazon",
                "price": 100.00,
            },
        )
        product_id = create_response.json()["id"]

        # Act
        response = await client.patch(
            f"/api/v1/products/{product_id}/price",
            json={"price": 89.90},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert float(data["price"]) == 89.90

    # -------------------------------------------------------------------------
    # DELETE /products/{id} - Remover produto
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_delete_product(self, client):
        """Deve remover produto existente."""
        # Arrange - Cria produto
        create_response = await client.post(
            "/api/v1/products",
            json={
                "name": "Para Deletar",
                "slug": "para-deletar-prod",
                "affiliate_url_raw": "https://amazon.com.br/dp/DEL",
                "affiliate_redirect_slug": "del-1",
                "platform": "amazon",
            },
        )
        product_id = create_response.json()["id"]

        # Act
        response = await client.delete(f"/api/v1/products/{product_id}")

        # Assert
        assert response.status_code == 200
        assert "sucesso" in response.json()["message"].lower()

        # Verifica que não existe mais
        get_response = await client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_product_not_found(self, client):
        """Deve retornar 404 ao deletar produto inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/products/{fake_id}")

        # Assert
        assert response.status_code == 404
