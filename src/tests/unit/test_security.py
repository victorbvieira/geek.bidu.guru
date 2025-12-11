"""
Testes unitarios para o modulo de seguranca.

Testa:
- Hashing de senhas
- Criacao e validacao de tokens JWT
"""

import pytest
from datetime import timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    """Testes para hashing de senhas."""

    def test_hash_password(self):
        """Deve gerar hash diferente da senha original."""
        password = "minha_senha_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_correct_password(self):
        """Deve retornar True para senha correta."""
        password = "minha_senha_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """Deve retornar False para senha incorreta."""
        password = "minha_senha_123"
        hashed = get_password_hash(password)

        assert verify_password("senha_errada", hashed) is False

    def test_hash_is_unique(self):
        """Hashes da mesma senha devem ser diferentes (salt)."""
        password = "minha_senha_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        # Mas ambos devem validar a mesma senha
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Testes para tokens JWT."""

    def test_create_access_token(self):
        """Deve criar access token valido."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        assert token is not None
        assert len(token) > 0
        assert "." in token  # JWT format: header.payload.signature

    def test_create_refresh_token(self):
        """Deve criar refresh token valido."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_refresh_token(subject=user_id)

        assert token is not None
        assert len(token) > 0

    def test_verify_access_token(self):
        """Deve verificar e decodificar access token."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        payload = verify_token(token, token_type="access")

        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"

    def test_verify_refresh_token(self):
        """Deve verificar e decodificar refresh token."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_refresh_token(subject=user_id)

        payload = verify_token(token, token_type="refresh")

        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_access_token_not_valid_as_refresh(self):
        """Access token nao deve ser aceito como refresh."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        # Tentar verificar como refresh deve falhar
        payload = verify_token(token, token_type="refresh")

        assert payload is None

    def test_refresh_token_not_valid_as_access(self):
        """Refresh token nao deve ser aceito como access."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_refresh_token(subject=user_id)

        # Tentar verificar como access deve falhar
        payload = verify_token(token, token_type="access")

        assert payload is None

    def test_invalid_token(self):
        """Token invalido deve retornar None."""
        payload = verify_token("token_invalido_123", token_type="access")

        assert payload is None

    def test_token_with_extra_claims(self):
        """Deve incluir claims extras no token."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        extra = {"role": "admin", "custom": "value"}

        token = create_access_token(subject=user_id, extra_claims=extra)
        payload = verify_token(token, token_type="access")

        assert payload is not None
        assert payload["role"] == "admin"
        assert payload["custom"] == "value"

    def test_token_with_custom_expiration(self):
        """Deve aceitar expiracao customizada."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        # Token com expiracao de 1 hora
        token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(hours=1),
        )

        payload = verify_token(token, token_type="access")

        assert payload is not None
        assert payload["sub"] == user_id
