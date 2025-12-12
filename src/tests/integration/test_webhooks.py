"""
Testes de integracao para os webhooks n8n.

Testa os endpoints de webhook usados pelo n8n para automacao.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def n8n_api_key(monkeypatch):
    """Define uma API Key de teste para o n8n."""
    test_key = "test-n8n-api-key-12345"
    monkeypatch.setattr("app.config.settings.n8n_api_key", test_key)
    return test_key


@pytest.fixture
async def webhook_automation_user(db_session: AsyncSession):
    """Cria usuario de automacao para testes de webhook."""
    from app.core.security import get_password_hash

    user = User(
        name="n8n Automation",
        email="automation-webhook@test.com",
        password_hash=get_password_hash("no-login"),
        role=UserRole.AUTOMATION,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# -----------------------------------------------------------------------------
# Testes de Health Check
# -----------------------------------------------------------------------------


class TestWebhookHealthCheck:
    """Testes do endpoint de health check."""

    async def test_health_check_without_api_key_returns_401(self, client):
        """Health check sem API Key retorna 401."""
        response = await client.get("/webhooks/n8n/health")
        # Pode ser 401 (sem header) ou 503 (API Key nao configurada)
        assert response.status_code in [401, 503]

    async def test_health_check_with_invalid_api_key_returns_401(
        self, client, n8n_api_key
    ):
        """Health check com API Key invalida retorna 401."""
        # n8n_api_key fixture configura a key no settings
        response = await client.get(
            "/webhooks/n8n/health",
            headers={"X-N8N-API-Key": "wrong-key"},
        )
        assert response.status_code == 401

    async def test_health_check_with_valid_api_key_returns_200(
        self, client, n8n_api_key
    ):
        """Health check com API Key valida retorna 200."""
        response = await client.get(
            "/webhooks/n8n/health",
            headers={"X-N8N-API-Key": n8n_api_key},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "timestamp" in data["data"]


# -----------------------------------------------------------------------------
# Testes de Criacao de Post
# -----------------------------------------------------------------------------


class TestWebhookCreatePost:
    """Testes do endpoint de criacao de post via webhook."""

    async def test_create_post_without_api_key_returns_401(self, client):
        """Criar post sem API Key retorna 401."""
        response = await client.post(
            "/webhooks/n8n/posts",
            json={
                "title": "Test Post",
                "slug": "test-post",
                "content": "A" * 100,
            },
        )
        assert response.status_code in [401, 503]

    async def test_create_post_without_automation_user_returns_503(
        self, client, n8n_api_key
    ):
        """Criar post sem usuario de automacao retorna 503."""
        response = await client.post(
            "/webhooks/n8n/posts",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "title": "Test Post",
                "slug": "test-post",
                "content": "A" * 100,
            },
        )
        assert response.status_code == 503
        assert "automacao" in response.json()["detail"].lower()

    async def test_create_post_with_valid_data_returns_200(
        self,
        client,
        n8n_api_key,
        webhook_automation_user,
    ):
        """Criar post com dados validos retorna 200."""
        # webhook_automation_user cria o usuario automation no banco
        response = await client.post(
            "/webhooks/n8n/posts",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "title": "Test Post via n8n",
                "slug": "test-post-n8n",
                "content": "Este e um post de teste criado via webhook n8n. " * 10,
                "tags": ["teste", "n8n", "automacao"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["slug"] == "test-post-n8n"

    async def test_create_post_with_duplicate_slug_returns_409(
        self,
        client,
        n8n_api_key,
        webhook_automation_user,
    ):
        """Criar post com slug duplicado retorna 409."""
        # webhook_automation_user cria o usuario automation no banco
        # Criar primeiro post
        await client.post(
            "/webhooks/n8n/posts",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "title": "Original Post",
                "slug": "duplicate-slug",
                "content": "A" * 100,
            },
        )

        # Tentar criar segundo post com mesmo slug
        response = await client.post(
            "/webhooks/n8n/posts",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "title": "Duplicate Post",
                "slug": "duplicate-slug",
                "content": "B" * 100,
            },
        )
        assert response.status_code == 409


# -----------------------------------------------------------------------------
# Testes de Criacao/Atualizacao de Produto
# -----------------------------------------------------------------------------


class TestWebhookCreateProduct:
    """Testes do endpoint de criacao de produto via webhook."""

    async def test_create_product_with_valid_data_returns_200(
        self, client, n8n_api_key
    ):
        """Criar produto com dados validos retorna 200."""
        response = await client.post(
            "/webhooks/n8n/products",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "name": "Produto Teste n8n",
                "slug": "produto-teste-n8n",
                "affiliate_url": "https://amazon.com.br/dp/TESTASIN?tag=geek",
                "current_price": 199.90,
                "tags": ["teste", "n8n"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["action"] == "created"

    async def test_update_existing_product_returns_200(self, client, n8n_api_key):
        """Atualizar produto existente retorna 200 com action=updated."""
        # Criar produto
        await client.post(
            "/webhooks/n8n/products",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "name": "Produto Original",
                "slug": "produto-update",
                "affiliate_url": "https://amazon.com.br/original",
                "current_price": 100.00,
            },
        )

        # Atualizar produto (mesmo slug)
        response = await client.post(
            "/webhooks/n8n/products",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "name": "Produto Atualizado",
                "slug": "produto-update",
                "affiliate_url": "https://amazon.com.br/updated",
                "current_price": 150.00,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["action"] == "updated"


# -----------------------------------------------------------------------------
# Testes de Atualizacao de Preco
# -----------------------------------------------------------------------------


class TestWebhookPriceUpdate:
    """Testes do endpoint de atualizacao de preco via webhook."""

    async def test_update_price_by_slug_returns_200(self, client, n8n_api_key):
        """Atualizar preco por slug retorna 200."""
        # Criar produto
        await client.post(
            "/webhooks/n8n/products",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "name": "Produto Preco",
                "slug": "produto-preco-test",
                "affiliate_url": "https://amazon.com.br/preco",
                "current_price": 200.00,
            },
        )

        # Atualizar preco
        response = await client.post(
            "/webhooks/n8n/price-update",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "slug": "produto-preco-test",
                "current_price": 179.90,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # O preco pode vir como string ou float, dependendo do banco
        assert float(data["data"]["old_price"]) == 200.00
        assert float(data["data"]["new_price"]) == 179.90

    async def test_update_price_product_not_found_returns_404(
        self, client, n8n_api_key
    ):
        """Atualizar preco de produto inexistente retorna 404."""
        response = await client.post(
            "/webhooks/n8n/price-update",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "slug": "produto-inexistente",
                "current_price": 99.90,
            },
        )
        assert response.status_code == 404

    async def test_update_price_without_identifier_returns_400(
        self, client, n8n_api_key
    ):
        """Atualizar preco sem identificador retorna 400."""
        response = await client.post(
            "/webhooks/n8n/price-update",
            headers={"X-N8N-API-Key": n8n_api_key},
            json={
                "current_price": 99.90,
            },
        )
        assert response.status_code == 400
