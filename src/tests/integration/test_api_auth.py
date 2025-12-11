"""
Testes de integracao para endpoints de Auth.

Testa o fluxo completo de autenticacao.
"""

import pytest

from app.core.security import get_password_hash


class TestAuthEndpoints:
    """Testes para /api/v1/auth."""

    # -------------------------------------------------------------------------
    # POST /auth/login - Login
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Deve retornar tokens para credenciais validas."""
        # Arrange - Cria usuario
        password = "senha123456"
        await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario Teste",
                "email": "login@example.com",
                "password": password,
                "role": "author",
            },
        )

        # Act - Login
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "login@example.com",
                "password": password,
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        """Deve retornar 401 para senha incorreta."""
        # Arrange - Cria usuario
        await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario Teste",
                "email": "wrong_pass@example.com",
                "password": "senha123456",
                "role": "author",
            },
        )

        # Act - Login com senha errada
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "wrong_pass@example.com",
                "password": "senhaerrada",
            },
        )

        # Assert
        assert response.status_code == 401
        assert "incorretos" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, client):
        """Deve retornar 401 para email nao cadastrado."""
        # Act
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "naoexiste@example.com",
                "password": "qualquersenha",
            },
        )

        # Assert
        assert response.status_code == 401

    # -------------------------------------------------------------------------
    # GET /auth/me - Dados do usuario autenticado
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_me_success(self, client):
        """Deve retornar dados do usuario autenticado."""
        # Arrange - Cria usuario e faz login
        password = "senha123456"
        await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario Me",
                "email": "me@example.com",
                "password": password,
                "role": "editor",
            },
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "me@example.com",
                "password": password,
            },
        )
        access_token = login_response.json()["access_token"]

        # Act - Busca dados do usuario
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["name"] == "Usuario Me"
        assert data["role"] == "editor"

    @pytest.mark.asyncio
    async def test_get_me_without_token(self, client):
        """Deve retornar 401 sem token."""
        # Act
        response = await client.get("/api/v1/auth/me")

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client):
        """Deve retornar 401 com token invalido."""
        # Act
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer token_invalido_123"},
        )

        # Assert
        assert response.status_code == 401

    # -------------------------------------------------------------------------
    # POST /auth/refresh - Renovar tokens
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client):
        """Deve renovar tokens com refresh token valido."""
        # Arrange - Cria usuario e faz login
        password = "senha123456"
        await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario Refresh",
                "email": "refresh@example.com",
                "password": password,
                "role": "author",
            },
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "refresh@example.com",
                "password": password,
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Act - Refresh tokens
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client):
        """Deve retornar 401 para refresh token invalido."""
        # Act
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "token_invalido_123"},
        )

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self, client):
        """Nao deve aceitar access token como refresh token."""
        # Arrange - Cria usuario e faz login
        password = "senha123456"
        await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario Access",
                "email": "access_as_refresh@example.com",
                "password": password,
                "role": "author",
            },
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "access_as_refresh@example.com",
                "password": password,
            },
        )
        access_token = login_response.json()["access_token"]

        # Act - Tenta usar access token como refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )

        # Assert - Deve falhar pois tipo do token e diferente
        assert response.status_code == 401
