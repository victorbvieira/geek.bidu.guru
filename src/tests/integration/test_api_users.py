"""
Testes de integração para endpoints de Users.

Testa o fluxo completo HTTP -> API -> Banco de dados.
"""

import pytest


class TestUserEndpoints:
    """Testes para /api/v1/users."""

    # -------------------------------------------------------------------------
    # POST /users - Criar usuário
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_user_success(self, client):
        """Deve criar um novo usuário com dados válidos."""
        # Arrange
        payload = {
            "name": "Novo Usuario",
            "email": "novo@example.com",
            "password": "senha123456",
            "role": "author",
        }

        # Act
        response = await client.post("/api/v1/users", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Novo Usuario"
        assert data["email"] == "novo@example.com"
        assert data["role"] == "author"
        assert "id" in data
        assert "password" not in data  # Senha não deve ser exposta

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client):
        """Deve retornar erro 400 ao criar usuário com email duplicado."""
        # Arrange - Cria primeiro usuário
        payload = {
            "name": "Usuario 1",
            "email": "duplicado@example.com",
            "password": "senha123456",
            "role": "author",
        }
        await client.post("/api/v1/users", json=payload)

        # Act - Tenta criar segundo com mesmo email
        payload["name"] = "Usuario 2"
        response = await client.post("/api/v1/users", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Email ja" in response.json()["detail"]  # "Email ja cadastrado" ou "Email ja existe"

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, client):
        """Deve retornar erro 422 para email inválido."""
        # Arrange
        payload = {
            "name": "Usuario",
            "email": "email-invalido",
            "password": "senha123456",
            "role": "author",
        }

        # Act
        response = await client.post("/api/v1/users", json=payload)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_password_too_short(self, client):
        """Deve retornar erro 422 para senha muito curta."""
        # Arrange
        payload = {
            "name": "Usuario",
            "email": "user@example.com",
            "password": "123",  # Muito curta
            "role": "author",
        }

        # Act
        response = await client.post("/api/v1/users", json=payload)

        # Assert
        assert response.status_code == 422

    # -------------------------------------------------------------------------
    # GET /users - Listar usuários
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_users_empty(self, client):
        """Deve retornar lista vazia quando não há usuários."""
        # Act
        response = await client.get("/api/v1/users")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, client):
        """Deve retornar usuários paginados."""
        # Arrange - Cria 3 usuários
        for i in range(3):
            await client.post(
                "/api/v1/users",
                json={
                    "name": f"Usuario {i}",
                    "email": f"user{i}@example.com",
                    "password": "senha123456",
                    "role": "author",
                },
            )

        # Act - Busca página 1 com 2 itens
        response = await client.get("/api/v1/users?page=1&per_page=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["pages"] == 2  # 3 itens / 2 por página = 2 páginas

    # -------------------------------------------------------------------------
    # GET /users/{id} - Buscar por ID
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client):
        """Deve retornar usuário por ID."""
        # Arrange - Cria usuário
        create_response = await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario Teste",
                "email": "teste@example.com",
                "password": "senha123456",
                "role": "editor",
            },
        )
        user_id = create_response.json()["id"]

        # Act
        response = await client.get(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == "Usuario Teste"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client):
        """Deve retornar 404 para ID inexistente."""
        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/users/{fake_id}")

        # Assert
        assert response.status_code == 404

    # -------------------------------------------------------------------------
    # PATCH /users/{id} - Atualizar usuário
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_update_user(self, client):
        """Deve atualizar dados do usuário."""
        # Arrange - Cria usuário
        create_response = await client.post(
            "/api/v1/users",
            json={
                "name": "Nome Original",
                "email": "original@example.com",
                "password": "senha123456",
                "role": "author",
            },
        )
        user_id = create_response.json()["id"]

        # Act - Atualiza nome
        response = await client.patch(
            f"/api/v1/users/{user_id}",
            json={"name": "Nome Atualizado"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nome Atualizado"
        assert data["email"] == "original@example.com"  # Inalterado

    @pytest.mark.asyncio
    async def test_update_user_email_duplicate(self, client):
        """Deve retornar erro ao atualizar email para um já existente."""
        # Arrange - Cria 2 usuários
        await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario 1",
                "email": "email1@example.com",
                "password": "senha123456",
                "role": "author",
            },
        )
        response2 = await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario 2",
                "email": "email2@example.com",
                "password": "senha123456",
                "role": "author",
            },
        )
        user2_id = response2.json()["id"]

        # Act - Tenta atualizar email do user2 para email do user1
        response = await client.patch(
            f"/api/v1/users/{user2_id}",
            json={"email": "email1@example.com"},
        )

        # Assert
        assert response.status_code == 400
        assert "Email ja" in response.json()["detail"]  # "Email ja cadastrado" ou "Email ja existe"

    # -------------------------------------------------------------------------
    # DELETE /users/{id} - Remover usuário
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_delete_user(self, client):
        """Deve remover usuário existente (requer admin)."""
        # Arrange - Cria um admin para autenticar
        admin_email = "admin_delete_test@example.com"
        await client.post(
            "/api/v1/users",
            json={
                "name": "Admin Delete Test",
                "email": admin_email,
                "password": "senha123456",
                "role": "admin",
            },
        )

        # Login como admin
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": admin_email, "password": "senha123456"},
        )
        admin_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Cria usuário para deletar
        create_response = await client.post(
            "/api/v1/users",
            json={
                "name": "Usuario para Deletar",
                "email": "deletar@example.com",
                "password": "senha123456",
                "role": "author",
            },
        )
        user_id = create_response.json()["id"]

        # Act - Deleta com token de admin
        response = await client.delete(f"/api/v1/users/{user_id}", headers=headers)

        # Assert
        assert response.status_code == 200
        assert "sucesso" in response.json()["message"].lower()

        # Verifica que não existe mais
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, client):
        """Deve retornar 404 ao deletar usuário inexistente (requer admin)."""
        # Arrange - Cria um admin para autenticar
        admin_email = "admin_delete_notfound@example.com"
        await client.post(
            "/api/v1/users",
            json={
                "name": "Admin Delete NotFound",
                "email": admin_email,
                "password": "senha123456",
                "role": "admin",
            },
        )

        # Login como admin
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": admin_email, "password": "senha123456"},
        )
        admin_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Act
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/users/{fake_id}", headers=headers)

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_requires_admin(self, client):
        """Deve retornar 403 quando usuário não-admin tenta deletar."""
        # Arrange - Cria um author (não-admin)
        author_email = "author_no_delete@example.com"
        await client.post(
            "/api/v1/users",
            json={
                "name": "Author No Delete",
                "email": author_email,
                "password": "senha123456",
                "role": "author",
            },
        )

        # Login como author
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": author_email, "password": "senha123456"},
        )
        author_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {author_token}"}

        # Act - Tenta deletar com token de author
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/users/{fake_id}", headers=headers)

        # Assert - Deve retornar 403 Forbidden
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_user_requires_authentication(self, client):
        """Deve retornar 401 quando não autenticado."""
        # Act - Tenta deletar sem token
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/users/{fake_id}")

        # Assert - Deve retornar 401 Unauthorized
        assert response.status_code == 401
