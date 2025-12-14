"""
Testes unitários para repositórios.

Este módulo testa as operações CRUD do BaseRepository e repositórios específicos.
Utiliza banco SQLite em memória para isolamento e velocidade.

Padrão de testes:
    - Arrange: Preparação dos dados e contexto
    - Act: Execução da operação a ser testada
    - Assert: Verificação do resultado esperado

Cobertura:
    - BaseRepository: get, get_by_field, get_multi, count, create, update, delete, exists
    - UserRepository: get_by_email, get_active_users, email_exists
"""

from uuid import uuid4

import pytest
import pytest_asyncio

from app.models import User
from app.models.user import UserRole
from app.repositories import UserRepository
from app.repositories.base import BaseRepository


# =============================================================================
# Testes do BaseRepository (usando User como modelo concreto)
# =============================================================================


class TestBaseRepository:
    """Testes para operações CRUD genéricas do BaseRepository."""

    @pytest_asyncio.fixture
    async def user_repo(self, db_session):
        """Cria repositório de usuários para testes."""
        return UserRepository(db_session)

    @pytest_asyncio.fixture
    async def sample_user(self, db_session) -> User:
        """
        Cria usuário de exemplo diretamente no banco.

        Usado para testes que precisam de um usuário pré-existente.
        """
        user = User(
            name="Usuario Teste",
            email="teste@example.com",
            password_hash="hashed_password_123",
            role=UserRole.AUTHOR,
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    # -------------------------------------------------------------------------
    # Testes de CREATE
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_deve_persistir_e_retornar_usuario(self, user_repo):
        """
        Deve criar um novo registro e retornar a instância com ID gerado.

        Arrange: Dados válidos para criação
        Act: Chama create() com os dados
        Assert: Registro criado com ID e dados corretos
        """
        # Arrange
        user_data = {
            "name": "Novo Usuario",
            "email": "novo@example.com",
            "password_hash": "hash_seguro_123",
            "role": UserRole.EDITOR,
        }

        # Act
        user = await user_repo.create(user_data)

        # Assert
        assert user.id is not None  # UUID foi gerado
        assert user.name == "Novo Usuario"
        assert user.email == "novo@example.com"
        assert user.role == UserRole.EDITOR

    @pytest.mark.asyncio
    async def test_create_deve_gerar_uuid_unico(self, user_repo):
        """Deve gerar UUIDs únicos para cada registro criado."""
        # Arrange & Act
        user1 = await user_repo.create({
            "name": "User 1",
            "email": "user1@example.com",
            "password_hash": "hash1",
        })
        user2 = await user_repo.create({
            "name": "User 2",
            "email": "user2@example.com",
            "password_hash": "hash2",
        })

        # Assert
        assert user1.id != user2.id

    # -------------------------------------------------------------------------
    # Testes de READ (get, get_by_field, get_multi)
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_deve_retornar_usuario_por_id(self, user_repo, sample_user):
        """
        Deve retornar o usuário quando existe no banco.

        Arrange: Usuário criado no banco (sample_user)
        Act: Busca pelo ID
        Assert: Retorna o mesmo usuário
        """
        # Act
        found = await user_repo.get(sample_user.id)

        # Assert
        assert found is not None
        assert found.id == sample_user.id
        assert found.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_deve_retornar_none_se_nao_existe(self, user_repo):
        """Deve retornar None para ID inexistente."""
        # Arrange
        fake_id = uuid4()

        # Act
        found = await user_repo.get(fake_id)

        # Assert
        assert found is None

    @pytest.mark.asyncio
    async def test_get_by_field_deve_retornar_usuario_por_email(
        self, user_repo, sample_user
    ):
        """Deve encontrar usuário por campo específico."""
        # Act
        found = await user_repo.get_by_field("email", sample_user.email)

        # Assert
        assert found is not None
        assert found.id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_by_field_deve_retornar_none_se_nao_existe(self, user_repo):
        """Deve retornar None se valor não existe."""
        # Act
        found = await user_repo.get_by_field("email", "inexistente@example.com")

        # Assert
        assert found is None

    @pytest.mark.asyncio
    async def test_get_multi_deve_retornar_lista_paginada(self, user_repo, db_session):
        """
        Deve retornar lista de registros com paginação.

        Arrange: Cria 5 usuários
        Act: Busca com limit=3, skip=1
        Assert: Retorna 3 usuários pulando o primeiro
        """
        # Arrange - Cria 5 usuários
        for i in range(5):
            user = User(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
            )
            db_session.add(user)
        await db_session.commit()

        # Act
        users = await user_repo.get_multi(skip=1, limit=3)

        # Assert
        assert len(users) == 3

    @pytest.mark.asyncio
    async def test_get_multi_deve_ordenar_por_campo(self, user_repo, db_session):
        """Deve ordenar resultados pelo campo especificado."""
        # Arrange - Cria usuários com nomes em ordem não-alfabética
        for name in ["Charlie", "Alice", "Bob"]:
            user = User(
                name=name,
                email=f"{name.lower()}@example.com",
                password_hash="hash",
            )
            db_session.add(user)
        await db_session.commit()

        # Act - Ordena por nome ascendente
        users = await user_repo.get_multi(order_by="name", desc=False)

        # Assert
        names = [u.name for u in users]
        assert names == ["Alice", "Bob", "Charlie"]

    # -------------------------------------------------------------------------
    # Testes de COUNT
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_count_deve_retornar_total_de_registros(self, user_repo, db_session):
        """Deve contar corretamente o número de registros."""
        # Arrange - Cria 3 usuários
        for i in range(3):
            user = User(
                name=f"User {i}",
                email=f"count{i}@example.com",
                password_hash=f"hash{i}",
            )
            db_session.add(user)
        await db_session.commit()

        # Act
        total = await user_repo.count()

        # Assert
        assert total == 3

    @pytest.mark.asyncio
    async def test_count_deve_retornar_zero_se_tabela_vazia(self, user_repo):
        """Deve retornar 0 para tabela vazia."""
        # Act
        total = await user_repo.count()

        # Assert
        assert total == 0

    # -------------------------------------------------------------------------
    # Testes de UPDATE
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_update_deve_atualizar_campos_especificados(
        self, user_repo, sample_user
    ):
        """
        Deve atualizar apenas os campos fornecidos.

        Arrange: Usuário existente
        Act: Atualiza nome e role
        Assert: Campos atualizados, outros inalterados
        """
        # Arrange
        original_email = sample_user.email

        # Act
        updated = await user_repo.update(
            sample_user,
            {"name": "Nome Atualizado", "role": UserRole.ADMIN}
        )

        # Assert
        assert updated.name == "Nome Atualizado"
        assert updated.role == UserRole.ADMIN
        assert updated.email == original_email  # Inalterado

    @pytest.mark.asyncio
    async def test_update_nao_deve_ignorar_campos_presentes(self, user_repo, sample_user):
        """
        Deve aplicar todos os campos presentes no dicionario.

        NOTA: O metodo update() aplica todos os campos do dicionario,
        incluindo valores None quando o campo permite. Campos NOT NULL
        devem receber valores validos.
        """
        # Arrange
        original_name = sample_user.name

        # Act - Passa dicionario vazio (sem campos para atualizar)
        updated = await user_repo.update(sample_user, {})

        # Assert - Nada deve mudar quando nao passamos campos
        assert updated.name == original_name

        # Act - Atualiza com valor especifico
        updated2 = await user_repo.update(sample_user, {"name": "Nome Modificado"})

        # Assert - Campo deve ser atualizado
        assert updated2.name == "Nome Modificado"

    # -------------------------------------------------------------------------
    # Testes de DELETE
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_delete_deve_remover_registro_e_retornar_true(
        self, user_repo, sample_user
    ):
        """
        Deve remover o registro e retornar True.

        Arrange: Usuário existente
        Act: Deleta pelo ID
        Assert: Retorna True e registro não existe mais
        """
        # Arrange
        user_id = sample_user.id

        # Act
        result = await user_repo.delete(user_id)

        # Assert
        assert result is True
        assert await user_repo.get(user_id) is None

    @pytest.mark.asyncio
    async def test_delete_deve_retornar_false_se_nao_existe(self, user_repo):
        """Deve retornar False para ID inexistente."""
        # Arrange
        fake_id = uuid4()

        # Act
        result = await user_repo.delete(fake_id)

        # Assert
        assert result is False

    # -------------------------------------------------------------------------
    # Testes de EXISTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_exists_deve_retornar_true_se_existe(self, user_repo, sample_user):
        """Deve retornar True para registro existente."""
        # Act
        result = await user_repo.exists(sample_user.id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_deve_retornar_false_se_nao_existe(self, user_repo):
        """Deve retornar False para ID inexistente."""
        # Arrange
        fake_id = uuid4()

        # Act
        result = await user_repo.exists(fake_id)

        # Assert
        assert result is False


# =============================================================================
# Testes específicos do UserRepository
# =============================================================================


class TestUserRepository:
    """Testes para métodos específicos do UserRepository."""

    @pytest_asyncio.fixture
    async def user_repo(self, db_session):
        """Cria repositório de usuários para testes."""
        return UserRepository(db_session)

    @pytest_asyncio.fixture
    async def users_fixture(self, db_session) -> list[User]:
        """Cria vários usuários para testes de listagem."""
        users = [
            User(
                name="Ativo 1",
                email="ativo1@example.com",
                password_hash="hash",
                is_active=True,
            ),
            User(
                name="Ativo 2",
                email="ativo2@example.com",
                password_hash="hash",
                is_active=True,
            ),
            User(
                name="Inativo",
                email="inativo@example.com",
                password_hash="hash",
                is_active=False,
            ),
        ]
        for user in users:
            db_session.add(user)
        await db_session.commit()
        return users

    @pytest.mark.asyncio
    async def test_get_by_email_deve_retornar_usuario(
        self, user_repo, users_fixture
    ):
        """Deve encontrar usuário por email."""
        # Act
        user = await user_repo.get_by_email("ativo1@example.com")

        # Assert
        assert user is not None
        assert user.name == "Ativo 1"

    @pytest.mark.asyncio
    async def test_get_by_email_deve_retornar_none_se_nao_existe(self, user_repo):
        """Deve retornar None para email não cadastrado."""
        # Act
        user = await user_repo.get_by_email("inexistente@example.com")

        # Assert
        assert user is None

    @pytest.mark.asyncio
    async def test_get_active_users_deve_filtrar_inativos(
        self, user_repo, users_fixture
    ):
        """Deve retornar apenas usuários ativos."""
        # Act
        active_users = await user_repo.get_active_users()

        # Assert
        assert len(active_users) == 2
        for user in active_users:
            assert user.is_active is True

    @pytest.mark.asyncio
    async def test_email_exists_deve_retornar_true_se_cadastrado(
        self, user_repo, users_fixture
    ):
        """Deve retornar True para email já cadastrado."""
        # Act
        exists = await user_repo.email_exists("ativo1@example.com")

        # Assert
        assert exists is True

    @pytest.mark.asyncio
    async def test_email_exists_deve_retornar_false_se_novo(self, user_repo):
        """Deve retornar False para email novo."""
        # Act
        exists = await user_repo.email_exists("novo@example.com")

        # Assert
        assert exists is False
