"""
Testes unitarios para o sistema de cache Redis.

Testa:
- Operacoes basicas (get, set, delete)
- Geracao de chaves
- Decorator de cache
- Cache de LLM
"""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.utils.cache import (
    cache_delete,
    cache_delete_pattern,
    cache_exists,
    cache_get,
    cache_key,
    cache_key_hash,
    cache_set,
    cached,
    get_cached_llm_response,
    cache_llm_response,
    hash_prompt,
)


# =============================================================================
# Testes de Geracao de Chaves
# =============================================================================


class TestCacheKeys:
    """Testes para funcoes de geracao de chaves."""

    def test_cache_key_single_arg(self):
        """Deve criar chave com um argumento."""
        key = cache_key("posts")
        assert key == "posts"

    def test_cache_key_multiple_args(self):
        """Deve criar chave com multiplos argumentos."""
        key = cache_key("posts", "list", "published")
        assert key == "posts:list:published"

    def test_cache_key_with_numbers(self):
        """Deve converter numeros para string."""
        key = cache_key("product", 123, "details")
        assert key == "product:123:details"

    def test_cache_key_hash_creates_hash(self):
        """Deve criar hash MD5."""
        key = cache_key_hash("prefix", "very long argument that should be hashed")
        assert key.startswith("prefix:")
        assert len(key.split(":")[1]) == 12  # MD5 truncado

    def test_cache_key_hash_consistent(self):
        """Hash deve ser consistente."""
        key1 = cache_key_hash("test", "same content")
        key2 = cache_key_hash("test", "same content")
        assert key1 == key2

    def test_hash_prompt_creates_hash(self):
        """hash_prompt deve criar MD5 do prompt."""
        hash1 = hash_prompt("system", "user")
        hash2 = hash_prompt("system", "user")
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 completo

    def test_hash_prompt_different_for_different_prompts(self):
        """hash_prompt deve ser diferente para prompts diferentes."""
        hash1 = hash_prompt("system1", "user")
        hash2 = hash_prompt("system2", "user")
        assert hash1 != hash2


# =============================================================================
# Testes de Operacoes Basicas (Mockadas)
# =============================================================================


class TestCacheOperations:
    """Testes para operacoes basicas de cache."""

    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis."""
        mock = AsyncMock()
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock(return_value=True)
        mock.setex = AsyncMock(return_value=True)
        mock.delete = AsyncMock(return_value=1)
        mock.exists = AsyncMock(return_value=1)
        mock.scan_iter = MagicMock()
        mock.ping = AsyncMock(return_value=True)
        return mock

    @pytest.mark.asyncio
    async def test_cache_get_returns_none_on_miss(self, mock_redis):
        """cache_get deve retornar None em miss."""
        mock_redis.get = AsyncMock(return_value=None)

        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            result = await cache_get("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_cache_get_deserializes_json(self, mock_redis):
        """cache_get deve deserializar JSON."""
        mock_redis.get = AsyncMock(return_value='{"key": "value"}')

        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            result = await cache_get("test_key")

        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_cache_set_serializes_json(self, mock_redis):
        """cache_set deve serializar para JSON."""
        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            result = await cache_set("key", {"data": "value"})

        assert result is True
        mock_redis.set.assert_called()

    @pytest.mark.asyncio
    async def test_cache_set_with_expire(self, mock_redis):
        """cache_set com expire deve usar setex."""
        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            result = await cache_set("key", "value", expire=timedelta(minutes=30))

        assert result is True
        mock_redis.setex.assert_called()

    @pytest.mark.asyncio
    async def test_cache_delete_returns_true_on_success(self, mock_redis):
        """cache_delete deve retornar True em sucesso."""
        mock_redis.delete = AsyncMock(return_value=1)

        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            result = await cache_delete("key")

        assert result is True

    @pytest.mark.asyncio
    async def test_cache_delete_returns_false_on_miss(self, mock_redis):
        """cache_delete deve retornar False se chave nao existia."""
        mock_redis.delete = AsyncMock(return_value=0)

        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            result = await cache_delete("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_cache_exists_returns_true(self, mock_redis):
        """cache_exists deve retornar True se existir."""
        mock_redis.exists = AsyncMock(return_value=1)

        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            result = await cache_exists("key")

        assert result is True

    @pytest.mark.asyncio
    async def test_cache_exists_returns_false(self, mock_redis):
        """cache_exists deve retornar False se nao existir."""
        mock_redis.exists = AsyncMock(return_value=0)

        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            result = await cache_exists("key")

        assert result is False


# =============================================================================
# Testes de Invalidacao por Padrao
# =============================================================================


class TestCachePattern:
    """Testes para invalidacao por padrao."""

    @pytest.mark.asyncio
    async def test_cache_delete_pattern_deletes_matching_keys(self):
        """Deve deletar chaves que correspondem ao padrao."""
        mock_redis = AsyncMock()

        async def mock_scan_iter(match):
            for key in ["posts:1", "posts:2", "posts:3"]:
                yield key

        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete = AsyncMock(return_value=3)

        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            count = await cache_delete_pattern("posts:*")

        assert count == 3
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_delete_pattern_returns_zero_on_no_match(self):
        """Deve retornar 0 se nenhuma chave corresponder."""
        mock_redis = AsyncMock()

        async def mock_scan_iter(match):
            return
            yield  # Generator vazio

        mock_redis.scan_iter = mock_scan_iter

        with patch("app.utils.cache.get_redis", return_value=mock_redis):
            count = await cache_delete_pattern("nonexistent:*")

        assert count == 0


# =============================================================================
# Testes do Decorator de Cache
# =============================================================================


class TestCachedDecorator:
    """Testes para decorator @cached."""

    @pytest.mark.asyncio
    async def test_cached_returns_from_cache_on_hit(self):
        """Deve retornar valor cacheado em hit."""
        # Simula cache hit
        with patch("app.utils.cache.cache_get", return_value={"cached": True}):
            with patch("app.utils.cache.cache_set", return_value=True):

                @cached(prefix="test", expire_minutes=60)
                async def my_func():
                    return {"computed": True}

                result = await my_func()

        assert result == {"cached": True}

    @pytest.mark.asyncio
    async def test_cached_computes_on_miss(self):
        """Deve computar e cachear em miss."""
        call_count = 0

        async def mock_cache_get(key):
            return None

        async def mock_cache_set(key, value, expire):
            return True

        with patch("app.utils.cache.cache_get", side_effect=mock_cache_get):
            with patch("app.utils.cache.cache_set", side_effect=mock_cache_set):

                @cached(prefix="test", expire_minutes=60)
                async def my_func():
                    nonlocal call_count
                    call_count += 1
                    return {"computed": True}

                result = await my_func()

        assert result == {"computed": True}
        assert call_count == 1


# =============================================================================
# Testes de Cache de LLM
# =============================================================================


class TestLLMCache:
    """Testes para cache de respostas LLM."""

    @pytest.mark.asyncio
    async def test_cache_llm_response(self):
        """Deve cachear resposta de LLM."""
        with patch("app.utils.cache.cache_set", return_value=True) as mock_set:
            result = await cache_llm_response(
                prompt_hash="abc123",
                response={"content": "Texto gerado"},
                expire_minutes=60,
            )

        assert result is True
        mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cached_llm_response_hit(self):
        """Deve retornar resposta cacheada."""
        with patch(
            "app.utils.cache.cache_get",
            return_value={"content": "Texto cacheado"},
        ):
            result = await get_cached_llm_response("abc123")

        assert result == {"content": "Texto cacheado"}

    @pytest.mark.asyncio
    async def test_get_cached_llm_response_miss(self):
        """Deve retornar None em miss."""
        with patch("app.utils.cache.cache_get", return_value=None):
            result = await get_cached_llm_response("nonexistent")

        assert result is None


# =============================================================================
# Testes de Tratamento de Erro
# =============================================================================


class TestCacheErrorHandling:
    """Testes para tratamento de erros."""

    @pytest.mark.asyncio
    async def test_cache_get_returns_none_on_connection_error(self):
        """cache_get deve retornar None em erro de conexao."""
        with patch(
            "app.utils.cache.get_redis",
            side_effect=ConnectionError("Redis offline"),
        ):
            result = await cache_get("key")

        assert result is None

    @pytest.mark.asyncio
    async def test_cache_set_returns_false_on_connection_error(self):
        """cache_set deve retornar False em erro de conexao."""
        with patch(
            "app.utils.cache.get_redis",
            side_effect=ConnectionError("Redis offline"),
        ):
            result = await cache_set("key", "value")

        assert result is False

    @pytest.mark.asyncio
    async def test_cache_delete_returns_false_on_connection_error(self):
        """cache_delete deve retornar False em erro de conexao."""
        with patch(
            "app.utils.cache.get_redis",
            side_effect=ConnectionError("Redis offline"),
        ):
            result = await cache_delete("key")

        assert result is False

    @pytest.mark.asyncio
    async def test_cache_exists_returns_false_on_connection_error(self):
        """cache_exists deve retornar False em erro de conexao."""
        with patch(
            "app.utils.cache.get_redis",
            side_effect=ConnectionError("Redis offline"),
        ):
            result = await cache_exists("key")

        assert result is False
