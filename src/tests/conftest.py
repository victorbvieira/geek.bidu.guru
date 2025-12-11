"""
Configuracao do pytest para testes do geek.bidu.guru.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import *  # noqa: F401, F403


# -----------------------------------------------------------------------------
# Fixtures de configuracao
# -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Cria event loop para testes async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# -----------------------------------------------------------------------------
# Banco de dados em memoria para testes
# -----------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Cria engine SQLite em memoria para testes."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Cria sessao de banco para cada teste."""
    async_session = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# -----------------------------------------------------------------------------
# Fixtures de dados de teste
# -----------------------------------------------------------------------------


@pytest.fixture
def user_data() -> dict[str, Any]:
    """Dados validos para criacao de usuario."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123",
        "role": "author",
    }


@pytest.fixture
def category_data() -> dict[str, Any]:
    """Dados validos para criacao de categoria."""
    return {
        "name": "Categoria Teste",
        "slug": "categoria-teste",
        "description": "Descricao da categoria de teste",
    }


@pytest.fixture
def post_data() -> dict[str, Any]:
    """Dados validos para criacao de post."""
    return {
        "type": "listicle",
        "title": "Top 10 Produtos Geek para 2024",
        "slug": "top-10-produtos-geek-2024",
        "subtitle": "Os melhores produtos para presentear",
        "content": "<p>Conteudo do post aqui...</p>",
        "seo_focus_keyword": "produtos geek",
        "seo_title": "Top 10 Produtos Geek 2024",
        "seo_description": "Descubra os melhores produtos geek para presentear em 2024.",
        "tags": ["geek", "presentes", "2024"],
        "status": "draft",
    }


@pytest.fixture
def product_data() -> dict[str, Any]:
    """Dados validos para criacao de produto."""
    return {
        "name": "Funko Pop Star Wars Darth Vader",
        "slug": "funko-pop-star-wars-darth-vader",
        "short_description": "Funko Pop do Darth Vader",
        "price": "149.90",
        "currency": "BRL",
        "price_range": "100-200",
        "affiliate_url_raw": "https://amazon.com.br/dp/B123456?tag=geekbidu-20",
        "affiliate_redirect_slug": "funko-vader-amazon",
        "platform": "amazon",
        "platform_product_id": "B123456",
        "categories": ["funko", "star-wars"],
        "tags": ["funko", "star-wars", "darth-vader"],
        "availability": "available",
        "rating": "4.5",
        "review_count": 150,
    }


@pytest.fixture
def newsletter_data() -> dict[str, Any]:
    """Dados validos para inscricao em newsletter."""
    return {
        "email": "subscriber@example.com",
        "name": "Newsletter Subscriber",
        "source": "homepage-popup",
    }
