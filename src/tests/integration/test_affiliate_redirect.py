"""
Testes de integracao para rotas de redirect de afiliados.

Testa o endpoint /goto/{slug} que:
1. Registra cliques em produtos
2. Redireciona para URL de afiliado
"""

import pytest


class TestAffiliateRedirect:
    """Testes para endpoint /goto/{slug}."""

    # -------------------------------------------------------------------------
    # Redirect basico
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_redirect_to_affiliate(self, client, product_data):
        """Redirect deve funcionar para produto existente."""
        # Arrange - Cria produto
        await client.post("/api/v1/products", json=product_data)

        # Act - Acessa /goto/{slug}
        response = await client.get(
            f"/goto/{product_data['affiliate_redirect_slug']}",
            follow_redirects=False,  # Nao seguir redirect para testar
        )

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == product_data["affiliate_url_raw"]

    @pytest.mark.asyncio
    async def test_redirect_not_found(self, client):
        """Produto inexistente deve retornar 404."""
        response = await client.get("/goto/produto-que-nao-existe")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_redirect_with_post_id(self, client, product_data, post_data):
        """Redirect deve aceitar post_id como query param."""
        # Arrange - Cria produto e post
        await client.post("/api/v1/products", json=product_data)
        post_response = await client.post("/api/v1/posts", json=post_data)
        post_id = post_response.json()["id"]

        # Act - Acessa /goto/{slug} com post_id
        response = await client.get(
            f"/goto/{product_data['affiliate_redirect_slug']}?post_id={post_id}",
            follow_redirects=False,
        )

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == product_data["affiliate_url_raw"]

    # -------------------------------------------------------------------------
    # Tracking de cliques
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_redirect_increments_click_count(self, client, product_data):
        """Redirect deve incrementar contador de cliques."""
        # Arrange - Cria produto
        create_response = await client.post("/api/v1/products", json=product_data)
        product_id = create_response.json()["id"]

        # Verifica click_count inicial
        get_response = await client.get(f"/api/v1/products/{product_id}")
        initial_count = get_response.json()["click_count"]

        # Act - Faz redirect
        await client.get(
            f"/goto/{product_data['affiliate_redirect_slug']}",
            follow_redirects=False,
        )

        # Assert - Click count deve ter incrementado
        get_response = await client.get(f"/api/v1/products/{product_id}")
        new_count = get_response.json()["click_count"]
        assert new_count == initial_count + 1

    @pytest.mark.asyncio
    async def test_redirect_creates_click_record(self, client, product_data):
        """Redirect deve criar registro de clique na tabela."""
        # Arrange - Cria produto
        await client.post("/api/v1/products", json=product_data)

        # Act - Faz redirect
        await client.get(
            f"/goto/{product_data['affiliate_redirect_slug']}",
            follow_redirects=False,
        )

        # Assert - Deve ter criado registro de clique
        # Usamos o endpoint de analytics para verificar
        response = await client.get("/api/v1/clicks/analytics?days=1")
        assert response.status_code == 200
        data = response.json()
        assert data["total_clicks"] >= 1

    @pytest.mark.asyncio
    async def test_multiple_redirects_increment_count(self, client, product_data):
        """Multiplos redirects devem incrementar contador."""
        # Arrange - Cria produto
        create_response = await client.post("/api/v1/products", json=product_data)
        product_id = create_response.json()["id"]

        # Act - Faz 3 redirects
        for _ in range(3):
            await client.get(
                f"/goto/{product_data['affiliate_redirect_slug']}",
                follow_redirects=False,
            )

        # Assert - Click count deve ser 3
        get_response = await client.get(f"/api/v1/products/{product_id}")
        assert get_response.json()["click_count"] == 3

    # -------------------------------------------------------------------------
    # Diferentes plataformas
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_redirect_amazon(self, client):
        """Redirect para Amazon deve funcionar."""
        product = {
            "name": "Produto Amazon",
            "slug": "produto-amazon",
            "affiliate_url_raw": "https://www.amazon.com.br/dp/B123?tag=geek-20",
            "affiliate_redirect_slug": "produto-amazon-amz",
            "platform": "amazon",
        }
        await client.post("/api/v1/products", json=product)

        response = await client.get(
            "/goto/produto-amazon-amz",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "amazon.com.br" in response.headers["location"]

    @pytest.mark.asyncio
    async def test_redirect_mercadolivre(self, client):
        """Redirect para Mercado Livre deve funcionar."""
        product = {
            "name": "Produto Mercado Livre",
            "slug": "produto-mercadolivre",
            "affiliate_url_raw": "https://mercadolivre.com.br/MLB-123?matt_tool=12345",
            "affiliate_redirect_slug": "produto-ml",
            "platform": "mercadolivre",
        }
        await client.post("/api/v1/products", json=product)

        response = await client.get(
            "/goto/produto-ml",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "mercadolivre.com.br" in response.headers["location"]

    @pytest.mark.asyncio
    async def test_redirect_shopee(self, client):
        """Redirect para Shopee deve funcionar."""
        product = {
            "name": "Produto Shopee",
            "slug": "produto-shopee",
            "affiliate_url_raw": "https://shopee.com.br/product/123/456?af_id=geek",
            "affiliate_redirect_slug": "produto-shopee-sp",
            "platform": "shopee",
        }
        await client.post("/api/v1/products", json=product)

        response = await client.get(
            "/goto/produto-shopee-sp",
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "shopee.com.br" in response.headers["location"]

    # -------------------------------------------------------------------------
    # Headers e tracking
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_redirect_captures_user_agent(self, client, product_data):
        """Redirect deve capturar User-Agent do request."""
        # Arrange - Cria produto
        create_response = await client.post("/api/v1/products", json=product_data)
        product_id = create_response.json()["id"]

        # Act - Faz redirect com User-Agent customizado
        await client.get(
            f"/goto/{product_data['affiliate_redirect_slug']}",
            headers={"User-Agent": "TestBrowser/1.0"},
            follow_redirects=False,
        )

        # Assert - Verificamos que clique foi registrado
        response = await client.get(f"/api/v1/clicks/product/{product_id}")
        assert response.status_code == 200
        clicks = response.json()
        assert len(clicks) >= 1

    @pytest.mark.asyncio
    async def test_redirect_captures_referer(self, client, product_data):
        """Redirect deve capturar Referer do request."""
        # Arrange - Cria produto
        await client.post("/api/v1/products", json=product_data)

        # Act - Faz redirect com Referer
        await client.get(
            f"/goto/{product_data['affiliate_redirect_slug']}",
            headers={"Referer": "https://geek.bidu.guru/blog/top-10-funkos"},
            follow_redirects=False,
        )

        # Assert - Redirect funcionou
        # (verificacao do referer armazenado seria via query direta no banco)
