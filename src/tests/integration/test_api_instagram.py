"""
Testes de integracao para endpoints de Instagram.

Testa o fluxo completo HTTP -> API -> Banco de dados para
os endpoints do Flow A (Post Diario Automatico).

NOTA: Todos os endpoints requerem autenticacao com role ADMIN ou AUTOMATION.
Os testes sem autenticacao devem retornar 401.
"""

import pytest


class TestInstagramAuthentication:
    """Testes de autenticacao dos endpoints Instagram."""

    @pytest.mark.asyncio
    async def test_random_product_requires_auth(self, client):
        """Deve retornar 401 sem token de autenticacao."""
        response = await client.get("/api/v1/instagram/product/random")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_mark_posted_requires_auth(self, client):
        """Deve retornar 401 sem token de autenticacao."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/api/v1/instagram/products/{fake_id}/mark-posted",
            json={"platform": "instagram"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_stats_requires_auth(self, client):
        """Deve retornar 401 sem token de autenticacao."""
        response = await client.get("/api/v1/instagram/stats")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_html_to_image_requires_auth(self, client):
        """Deve retornar 401 sem token de autenticacao."""
        response = await client.post(
            "/api/v1/instagram/utils/html-to-image",
            json={"html": "<html></html>", "width": 100, "height": 100},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_resize_image_requires_auth(self, client):
        """Deve retornar 401 sem token de autenticacao."""
        from io import BytesIO
        from PIL import Image

        img = Image.new("RGB", (10, 10), color="red")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        response = await client.post(
            "/api/v1/instagram/utils/resize-image",
            files={"file": ("test.png", buffer, "image/png")},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_template_requires_auth(self, client):
        """Deve retornar 401 sem token de autenticacao."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/instagram/template/{fake_id}")
        assert response.status_code == 401


class TestInstagramEndpointsAuthenticated:
    """Testes para /api/v1/instagram com autenticacao."""

    @pytest.fixture
    async def auth_headers(self, client):
        """Obtem headers de autenticacao para usuario automation."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "automation@geek.bidu.guru",
                "password": "automation123",
            },
        )
        if response.status_code != 200:
            pytest.skip("Usuario automation nao configurado")
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    async def product_with_image(self, client, auth_headers):
        """Cria produto com imagem para testes de posting."""
        payload = {
            "name": "Headset Gamer RGB Test",
            "slug": "headset-gamer-rgb-test-auth",
            "short_description": "Headset com iluminacao RGB",
            "price": 199.90,
            "main_image_url": "https://example.com/headset.jpg",
            "affiliate_url_raw": "https://amazon.com.br/dp/HEADSET123AUTH",
            "affiliate_redirect_slug": "headset-gamer-test-auth",
            "platform": "amazon",
            "availability": "available",
            "instagram_headline": "OFERTA IMPERDIVEL!",
            "instagram_title": "Headset Gamer RGB",
            "instagram_badge": "NOVO!",
            "instagram_hashtags": ["gamer", "headset", "rgb"],
        }
        response = await client.post("/api/v1/products", json=payload)
        assert response.status_code == 201
        return response.json()

    @pytest.fixture
    async def product_without_image(self, client):
        """Cria produto sem imagem."""
        payload = {
            "name": "Mouse Simples Test Auth",
            "slug": "mouse-simples-test-auth",
            "affiliate_url_raw": "https://amazon.com.br/dp/MOUSE123AUTH",
            "affiliate_redirect_slug": "mouse-simples-test-auth",
            "platform": "amazon",
            "availability": "available",
        }
        response = await client.post("/api/v1/products", json=payload)
        assert response.status_code == 201
        return response.json()

    # -------------------------------------------------------------------------
    # GET /instagram/product/random
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_random_product_success(
        self, client, auth_headers, product_with_image
    ):
        """Deve retornar produto elegivel para posting."""
        response = await client.get(
            "/api/v1/instagram/product/random",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "main_image_url" in data
        assert "instagram_headline" in data
        assert "instagram_hashtags" in data

    @pytest.mark.asyncio
    async def test_get_random_product_no_available(self, client, auth_headers):
        """Deve retornar 404 quando nao ha produtos elegiveis."""
        response = await client.get(
            "/api/v1/instagram/product/random",
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "Nenhum produto disponivel" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_random_product_includes_instagram_metadata(
        self, client, auth_headers, product_with_image
    ):
        """Deve incluir metadados Instagram pre-configurados."""
        response = await client.get(
            "/api/v1/instagram/product/random",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["instagram_headline"] == "OFERTA IMPERDIVEL!"
        assert data["instagram_badge"] == "NOVO!"
        assert "gamer" in data["instagram_hashtags"]

    # -------------------------------------------------------------------------
    # PATCH /instagram/products/{id}/mark-posted
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_mark_posted_success(
        self, client, auth_headers, product_with_image
    ):
        """Deve marcar produto como postado."""
        product_id = product_with_image["id"]
        payload = {
            "platform": "instagram",
            "post_url": "https://instagram.com/p/abc123",
            "caption": "Confira essa oferta!",
        }

        response = await client.patch(
            f"/api/v1/instagram/products/{product_id}/mark-posted",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["product_id"] == product_id
        assert data["post_count"] == 1
        assert "last_post_date" in data

    @pytest.mark.asyncio
    async def test_mark_posted_increments_count(
        self, client, auth_headers, product_with_image
    ):
        """Deve incrementar post_count a cada chamada."""
        product_id = product_with_image["id"]
        payload = {"platform": "instagram"}

        for i in range(1, 4):
            response = await client.patch(
                f"/api/v1/instagram/products/{product_id}/mark-posted",
                json=payload,
                headers=auth_headers,
            )
            assert response.status_code == 200
            assert response.json()["post_count"] == i

    @pytest.mark.asyncio
    async def test_mark_posted_product_not_found(self, client, auth_headers):
        """Deve retornar 404 para produto inexistente."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/api/v1/instagram/products/{fake_id}/mark-posted",
            json={"platform": "instagram"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # GET /instagram/stats
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_stats(self, client, auth_headers):
        """Deve retornar estatisticas de posting."""
        response = await client.get(
            "/api/v1/instagram/stats",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "available_for_posting" in data
        assert "total_products" in data
        assert "days_since_last_post" in data

    @pytest.mark.asyncio
    async def test_get_stats_with_products(
        self, client, auth_headers, product_with_image
    ):
        """Deve contar produtos elegiveis corretamente."""
        response = await client.get(
            "/api/v1/instagram/stats",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["available_for_posting"] >= 1


class TestProductInstagramMetadata:
    """Testes para campos de metadados Instagram em produtos."""

    @pytest.mark.asyncio
    async def test_create_product_with_instagram_metadata(self, client):
        """Deve criar produto com metadados Instagram."""
        payload = {
            "name": "Produto com Instagram Metadata",
            "slug": "produto-com-instagram-metadata",
            "affiliate_url_raw": "https://amazon.com.br/dp/TESTMETA",
            "affiliate_redirect_slug": "produto-ig-meta-test",
            "platform": "amazon",
            "instagram_headline": "SUPER OFERTA!",
            "instagram_title": "Titulo Instagram",
            "instagram_badge": "DESTAQUE",
            "instagram_caption": "Caption de teste para Instagram",
            "instagram_hashtags": ["teste", "produto", "geek"],
        }

        response = await client.post("/api/v1/products", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["instagram_headline"] == "SUPER OFERTA!"
        assert data["instagram_title"] == "Titulo Instagram"
        assert data["instagram_badge"] == "DESTAQUE"
        assert data["instagram_caption"] == "Caption de teste para Instagram"
        assert data["instagram_hashtags"] == ["teste", "produto", "geek"]

    @pytest.mark.asyncio
    async def test_update_product_instagram_metadata(self, client):
        """Deve atualizar metadados Instagram do produto."""
        # Cria produto
        create_payload = {
            "name": "Produto Update Instagram Meta",
            "slug": "produto-update-instagram-meta",
            "affiliate_url_raw": "https://amazon.com.br/dp/UPDATEMETA",
            "affiliate_redirect_slug": "produto-upd-ig-meta",
            "platform": "amazon",
        }
        create_response = await client.post("/api/v1/products", json=create_payload)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]

        # Atualiza metadados Instagram
        update_payload = {
            "instagram_headline": "NOVA HEADLINE",
            "instagram_hashtags": ["atualizado", "novo"],
        }
        update_response = await client.patch(
            f"/api/v1/products/{product_id}",
            json=update_payload,
        )
        assert update_response.status_code == 200

        data = update_response.json()
        assert data["instagram_headline"] == "NOVA HEADLINE"
        assert data["instagram_hashtags"] == ["atualizado", "novo"]

    @pytest.mark.asyncio
    async def test_product_response_includes_instagram_fields(self, client):
        """Deve incluir campos Instagram no response."""
        payload = {
            "name": "Produto Response Fields Test",
            "slug": "produto-response-fields-test",
            "affiliate_url_raw": "https://amazon.com.br/dp/RESPFIELDS",
            "affiliate_redirect_slug": "produto-resp-fields",
            "platform": "amazon",
        }

        response = await client.post("/api/v1/products", json=payload)
        assert response.status_code == 201

        data = response.json()
        # Campos devem existir mesmo que nulos
        assert "instagram_headline" in data
        assert "instagram_title" in data
        assert "instagram_badge" in data
        assert "instagram_caption" in data
        assert "instagram_hashtags" in data
