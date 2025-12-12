"""
Utilitarios de cache com Redis.

Funcionalidades:
- Cache de valores com TTL
- Decorator para caching de funcoes async
- Invalidacao por padrao
- Serialization JSON automatica
"""

import functools
import hashlib
import json
import logging
from datetime import timedelta
from typing import Any, Callable, Optional, TypeVar

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Cliente Redis Global
# =============================================================================


_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    Retorna cliente Redis, criando se necessario.

    Returns:
        Cliente Redis conectado

    Raises:
        ConnectionError: Se nao conseguir conectar ao Redis
    """
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            # Testa conexao
            await _redis_client.ping()
            logger.info(f"Redis conectado: {settings.redis_url}")
        except Exception as e:
            logger.warning(f"Falha ao conectar ao Redis: {e}. Cache desabilitado.")
            _redis_client = None
            raise ConnectionError(f"Nao foi possivel conectar ao Redis: {e}")

    return _redis_client


async def close_redis() -> None:
    """Fecha conexao com Redis."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis desconectado")


# =============================================================================
# Operacoes Basicas de Cache
# =============================================================================


async def cache_get(key: str) -> Optional[Any]:
    """
    Busca valor no cache.

    Args:
        key: Chave do cache

    Returns:
        Valor deserializado ou None se nao encontrado
    """
    try:
        client = await get_redis()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except ConnectionError:
        return None
    except Exception as e:
        logger.warning(f"Erro ao buscar cache [{key}]: {e}")
        return None


async def cache_set(
    key: str,
    value: Any,
    expire: Optional[timedelta] = None,
) -> bool:
    """
    Salva valor no cache.

    Args:
        key: Chave do cache
        value: Valor a salvar (sera serializado para JSON)
        expire: Tempo de expiracao (None = sem expiracao)

    Returns:
        True se salvou, False se erro
    """
    try:
        client = await get_redis()
        serialized = json.dumps(value, default=str, ensure_ascii=False)

        if expire:
            await client.setex(key, expire, serialized)
        else:
            await client.set(key, serialized)

        return True
    except ConnectionError:
        return False
    except Exception as e:
        logger.warning(f"Erro ao salvar cache [{key}]: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """
    Remove valor do cache.

    Args:
        key: Chave do cache

    Returns:
        True se removeu, False se erro ou nao existia
    """
    try:
        client = await get_redis()
        result = await client.delete(key)
        return result > 0
    except ConnectionError:
        return False
    except Exception as e:
        logger.warning(f"Erro ao deletar cache [{key}]: {e}")
        return False


async def cache_delete_pattern(pattern: str) -> int:
    """
    Remove valores que correspondem ao padrao.

    Args:
        pattern: Padrao glob (ex: "posts:*", "product:123:*")

    Returns:
        Numero de chaves deletadas
    """
    try:
        client = await get_redis()
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            deleted = await client.delete(*keys)
            logger.info(f"Cache invalidado: {deleted} chaves removidas (padrao: {pattern})")
            return deleted

        return 0
    except ConnectionError:
        return 0
    except Exception as e:
        logger.warning(f"Erro ao deletar cache por padrao [{pattern}]: {e}")
        return 0


async def cache_exists(key: str) -> bool:
    """
    Verifica se chave existe no cache.

    Args:
        key: Chave do cache

    Returns:
        True se existe, False caso contrario
    """
    try:
        client = await get_redis()
        return await client.exists(key) > 0
    except ConnectionError:
        return False
    except Exception as e:
        logger.warning(f"Erro ao verificar cache [{key}]: {e}")
        return False


# =============================================================================
# Funcoes de Chave
# =============================================================================


def cache_key(*args: Any) -> str:
    """
    Gera chave de cache a partir de argumentos.

    Args:
        *args: Partes da chave

    Returns:
        Chave formatada (ex: "posts:list:published")
    """
    return ":".join(str(arg) for arg in args)


def cache_key_hash(*args: Any) -> str:
    """
    Gera chave de cache com hash (para argumentos longos).

    Args:
        *args: Partes da chave (sera calculado hash)

    Returns:
        Chave com hash MD5
    """
    content = ":".join(str(arg) for arg in args)
    hash_val = hashlib.md5(content.encode()).hexdigest()[:12]
    return f"{args[0]}:{hash_val}" if args else hash_val


# =============================================================================
# Decorator de Cache
# =============================================================================


T = TypeVar("T")


def cached(
    prefix: str,
    expire_minutes: int = 60,
    key_builder: Optional[Callable[..., str]] = None,
):
    """
    Decorator que cacheia resultado de funcao async.

    Args:
        prefix: Prefixo da chave de cache
        expire_minutes: Tempo de expiracao em minutos (default: 60)
        key_builder: Funcao customizada para construir chave

    Usage:
        @cached(prefix="posts", expire_minutes=30)
        async def get_published_posts(limit: int = 20) -> list[Post]:
            ...

        @cached(
            prefix="post",
            expire_minutes=60,
            key_builder=lambda slug: f"post:slug:{slug}"
        )
        async def get_post_by_slug(slug: str) -> Post:
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Construir chave de cache
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                # Chave padrao: prefix:func_name:args_hash
                key_parts = [prefix, func.__name__]
                if args:
                    key_parts.extend(str(a) for a in args)
                if kwargs:
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key = cache_key(*key_parts)

            # Tentar buscar do cache
            cached_value = await cache_get(key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {key}")
                return cached_value

            logger.debug(f"Cache MISS: {key}")

            # Executar funcao
            result = await func(*args, **kwargs)

            # Cachear resultado
            await cache_set(key, result, timedelta(minutes=expire_minutes))

            return result

        return wrapper

    return decorator


# =============================================================================
# Cache Especifico para LLM
# =============================================================================


async def cache_llm_response(
    prompt_hash: str,
    response: dict[str, Any],
    expire_minutes: int = 60,
) -> bool:
    """
    Cacheia resposta de LLM.

    Args:
        prompt_hash: Hash do prompt (system + user)
        response: Resposta do LLM
        expire_minutes: Tempo de expiracao

    Returns:
        True se cacheou, False se erro
    """
    key = cache_key("llm", "response", prompt_hash)
    return await cache_set(key, response, timedelta(minutes=expire_minutes))


async def get_cached_llm_response(prompt_hash: str) -> Optional[dict[str, Any]]:
    """
    Busca resposta cacheada de LLM.

    Args:
        prompt_hash: Hash do prompt

    Returns:
        Resposta cacheada ou None
    """
    key = cache_key("llm", "response", prompt_hash)
    return await cache_get(key)


def hash_prompt(system: str, user: str) -> str:
    """
    Gera hash de prompt para cache de LLM.

    Args:
        system: System prompt
        user: User prompt

    Returns:
        Hash MD5 do prompt combinado
    """
    combined = f"{system}|||{user}"
    return hashlib.md5(combined.encode()).hexdigest()


# =============================================================================
# Health Check
# =============================================================================


async def redis_health_check() -> dict[str, Any]:
    """
    Verifica saude do Redis.

    Returns:
        Dict com status, latencia e info
    """
    try:
        import time

        client = await get_redis()

        # Medir latencia
        start = time.time()
        await client.ping()
        latency_ms = (time.time() - start) * 1000

        # Info basica
        info = await client.info("memory")

        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "used_memory": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", "N/A"),
        }

    except ConnectionError:
        return {"status": "disconnected", "error": "Redis nao disponivel"}

    except Exception as e:
        return {"status": "error", "error": str(e)}
