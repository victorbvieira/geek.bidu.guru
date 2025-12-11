"""
Testes de integração para endpoints de Newsletter.

Testa o fluxo completo HTTP -> API -> Banco de dados.
"""

import pytest


class TestNewsletterEndpoints:
    """Testes para /api/v1/newsletter."""

    # -------------------------------------------------------------------------
    # POST /newsletter/subscribe - Inscrever
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_subscribe_success(self, client):
        """Deve inscrever um novo email na newsletter."""
        # Arrange
        payload = {
            "email": "novo@example.com",
            "name": "Novo Inscrito",
        }

        # Act
        response = await client.post("/api/v1/newsletter/subscribe", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "novo@example.com"
        assert "sucesso" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_subscribe_already_subscribed(self, client):
        """Deve retornar mensagem informativa para email já inscrito."""
        # Arrange - Inscreve primeiro
        payload = {"email": "duplicado@example.com"}
        await client.post("/api/v1/newsletter/subscribe", json=payload)

        # Act - Tenta inscrever novamente
        response = await client.post("/api/v1/newsletter/subscribe", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "ja esta inscrito" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_subscribe_reactivate(self, client):
        """Deve reativar inscrição de email que foi desinscrito."""
        # Arrange - Inscreve e desinscreve
        email = "reativar@example.com"
        await client.post("/api/v1/newsletter/subscribe", json={"email": email})
        await client.post(f"/api/v1/newsletter/unsubscribe?email={email}")

        # Act - Reinscreve
        response = await client.post(
            "/api/v1/newsletter/subscribe", json={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "reativada" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_subscribe_invalid_email(self, client):
        """Deve retornar erro 422 para email inválido."""
        # Arrange
        payload = {"email": "email-invalido"}

        # Act
        response = await client.post("/api/v1/newsletter/subscribe", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_subscribe_minimal_data(self, client):
        """Deve inscrever apenas com email (nome é opcional)."""
        # Arrange
        payload = {"email": "minimal@example.com"}

        # Act
        response = await client.post("/api/v1/newsletter/subscribe", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "minimal@example.com"

    # -------------------------------------------------------------------------
    # POST /newsletter/unsubscribe - Desinscrever
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_unsubscribe_success(self, client):
        """Deve desinscrever email existente."""
        # Arrange - Inscreve primeiro
        email = "para-desinscrever@example.com"
        await client.post("/api/v1/newsletter/subscribe", json={"email": email})

        # Act
        response = await client.post(f"/api/v1/newsletter/unsubscribe?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "sucesso" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_unsubscribe_not_found(self, client):
        """Deve retornar 404 para email não cadastrado."""
        # Act
        response = await client.post(
            "/api/v1/newsletter/unsubscribe?email=inexistente@example.com"
        )

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unsubscribe_already_unsubscribed(self, client):
        """Deve retornar mensagem informativa se já desinscrito."""
        # Arrange - Inscreve e desinscreve
        email = "ja-desinscrito@example.com"
        await client.post("/api/v1/newsletter/subscribe", json={"email": email})
        await client.post(f"/api/v1/newsletter/unsubscribe?email={email}")

        # Act - Tenta desinscrever novamente
        response = await client.post(f"/api/v1/newsletter/unsubscribe?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "ja estava desinscrito" in data["message"].lower()

    # -------------------------------------------------------------------------
    # GET /newsletter/subscribers - Listar inscritos
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_subscribers_empty(self, client):
        """Deve retornar lista vazia quando não há inscritos."""
        # Act
        response = await client.get("/api/v1/newsletter/subscribers")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_subscribers_with_pagination(self, client):
        """Deve retornar inscritos paginados."""
        # Arrange - Cria 5 inscritos
        for i in range(5):
            await client.post(
                "/api/v1/newsletter/subscribe",
                json={"email": f"inscrito{i}@example.com"},
            )

        # Act - Busca página 1 com 3 itens
        response = await client.get("/api/v1/newsletter/subscribers?page=1&per_page=3")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5

    @pytest.mark.asyncio
    async def test_list_subscribers_active_only(self, client):
        """Deve filtrar apenas inscritos ativos por padrão."""
        # Arrange - Cria inscrito ativo e inativo
        await client.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "ativo@example.com"},
        )
        await client.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "inativo@example.com"},
        )
        await client.post("/api/v1/newsletter/unsubscribe?email=inativo@example.com")

        # Act - Busca apenas ativos (padrão)
        response = await client.get("/api/v1/newsletter/subscribers?active_only=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["email"] == "ativo@example.com"

    @pytest.mark.asyncio
    async def test_list_subscribers_include_inactive(self, client):
        """Deve incluir inativos quando solicitado."""
        # Arrange - Cria inscrito ativo e inativo
        await client.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "ativo2@example.com"},
        )
        await client.post(
            "/api/v1/newsletter/subscribe",
            json={"email": "inativo2@example.com"},
        )
        await client.post("/api/v1/newsletter/unsubscribe?email=inativo2@example.com")

        # Act - Busca todos (incluindo inativos)
        response = await client.get("/api/v1/newsletter/subscribers?active_only=false")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    # -------------------------------------------------------------------------
    # GET /newsletter/stats - Estatísticas
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_newsletter_stats_empty(self, client):
        """Deve retornar estatísticas zeradas sem inscritos."""
        # Act
        response = await client.get("/api/v1/newsletter/stats")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_subscribers"] == 0

    @pytest.mark.asyncio
    async def test_get_newsletter_stats_with_data(self, client):
        """Deve retornar estatísticas corretas com inscritos."""
        # Arrange - Cria inscritos
        for i in range(3):
            await client.post(
                "/api/v1/newsletter/subscribe",
                json={"email": f"stats{i}@example.com"},
            )
        # Desinscreve um
        await client.post("/api/v1/newsletter/unsubscribe?email=stats0@example.com")

        # Act
        response = await client.get("/api/v1/newsletter/stats")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_subscribers"] == 3  # Total inclui inativos
        assert data["active_subscribers"] == 2  # Apenas ativos
        assert data["unsubscribed"] == 1  # Desinscritos
