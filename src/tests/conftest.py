"""
Configuracao do pytest para testes do geek.bidu.guru.

Suporta dois modos de banco de dados:
    - SQLite em memoria (padrao): Rapido, isolado, mas sem suporte a JSONB
    - PostgreSQL de dev: Completo, mas mais lento e requer conexao

Para rodar com PostgreSQL:
    pytest --use-postgres

Para rodar apenas testes que requerem PostgreSQL:
    pytest -m postgresql --use-postgres
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import *  # noqa: F401, F403


def pytest_addoption(parser):
    """Adiciona opcao --use-postgres para rodar testes com PostgreSQL."""
    parser.addoption(
        "--use-postgres",
        action="store_true",
        default=False,
        help="Usar PostgreSQL de dev ao inves de SQLite em memoria",
    )


def pytest_configure(config):
    """Configura markers customizados."""
    config.addinivalue_line(
        "markers",
        "postgresql: marca testes que requerem PostgreSQL (JSONB, etc)",
    )


def pytest_collection_modifyitems(config, items):
    """
    Pula testes marcados com @pytest.mark.postgresql se --use-postgres nao foi passado.
    Remove o skip de testes de categoria quando usando PostgreSQL.
    """
    if config.getoption("--use-postgres"):
        # Usando PostgreSQL - remove skips de testes que requerem PostgreSQL
        for item in items:
            # Remove skip markers que foram adicionados por causa do SQLite
            item.own_markers = [
                m for m in item.own_markers
                if not (m.name == "skip" and "JSONB" in str(m.kwargs.get("reason", "")))
            ]
    else:
        # Usando SQLite - pula testes marcados como postgresql
        skip_postgres = pytest.mark.skip(
            reason="Requer --use-postgres para rodar com PostgreSQL"
        )
        for item in items:
            if "postgresql" in item.keywords:
                item.add_marker(skip_postgres)


# -----------------------------------------------------------------------------
# Fixtures de configuracao
# -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Cria event loop para testes async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def use_postgres(request) -> bool:
    """Retorna True se --use-postgres foi passado."""
    return request.config.getoption("--use-postgres")


# -----------------------------------------------------------------------------
# Banco de dados para testes
# -----------------------------------------------------------------------------


def pytest_sessionstart(session):
    """
    Hook chamado no inicio da sessao de testes.

    Limpa todas as tabelas do PostgreSQL se --use-postgres foi passado.

    SEGURANCA: Verifica que estamos em ambiente de desenvolvimento antes de
    limpar o banco. NUNCA executa em producao!
    """
    if not session.config.getoption("--use-postgres", default=False):
        return

    from dotenv import load_dotenv
    from sqlalchemy import create_engine, text
    load_dotenv()

    # VERIFICACAO DE SEGURANCA: Impede execucao em producao
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment not in ("development", "dev", "test", "testing"):
        print(f"\n🚫 BLOQUEADO: Testes com --use-postgres so podem rodar em "
              f"ambiente de desenvolvimento!")
        print(f"   ENVIRONMENT atual: {environment}")
        print(f"   Configure ENVIRONMENT=development no .env para testes.\n")
        pytest.exit("Testes bloqueados por seguranca - ambiente nao e development", 1)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return

    # VERIFICACAO ADICIONAL: Impede uso de banco de producao
    if "prod" in database_url.lower():
        print(f"\n🚫 BLOQUEADO: DATABASE_URL parece ser de producao!")
        print(f"   Nao e permitido rodar testes com --use-postgres em banco de producao.")
        print(f"   Use um banco de desenvolvimento ou teste.\n")
        pytest.exit("Testes bloqueados por seguranca - banco de producao detectado", 1)

    print(f"\n✅ Ambiente: {environment} - OK para testes com PostgreSQL")

    # Usa driver sincrono para o hook
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    try:
        engine = create_engine(sync_url)
        with engine.begin() as conn:
            # Lista de tabelas para limpar (ordem correta para evitar erros de FK)
            # Primeiro tabelas com FKs, depois tabelas base
            tables = [
                "affiliate_clicks",
                "post_products",
                "posts",
                "products",
                "categories",
                "newsletter_signups",
                "occasions",
                "redirects",
                "sessions",
                "users",
            ]
            for table in tables:
                try:
                    conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                except Exception:
                    pass
        engine.dispose()
        print("\n🧹 Tabelas limpas para testes com PostgreSQL\n")
    except Exception as e:
        print(f"\n⚠️ Erro ao limpar tabelas: {e}\n")


@pytest_asyncio.fixture(scope="function")
async def async_engine(use_postgres):
    """
    Cria engine de banco de dados para testes.

    - Com --use-postgres: Usa DATABASE_URL (tabelas limpas no inicio da sessao)
    - Sem --use-postgres: Usa SQLite em memoria (padrao)
    """
    if use_postgres:
        # Usa PostgreSQL de dev
        from dotenv import load_dotenv
        load_dotenv()

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            pytest.skip("DATABASE_URL nao configurada no .env")

        # Converte para async se necessario
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )

        engine = create_async_engine(database_url, echo=False)

        yield engine

        await engine.dispose()
    else:
        # Usa SQLite em memoria (padrao)
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


async def _truncate_all_tables(session):
    """Limpa todas as tabelas do banco (para isolamento de testes)."""
    from sqlalchemy import text

    tables = [
        "affiliate_clicks",
        "post_products",
        "posts",
        "products",
        "categories",
        "newsletter_signups",
        "occasions",
        "redirects",
        "sessions",
        "users",
    ]
    for table in tables:
        try:
            await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
        except Exception:
            pass
    await session.commit()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine, use_postgres) -> AsyncGenerator[AsyncSession, None]:
    """
    Cria sessao de banco para cada teste com isolamento.

    Para PostgreSQL: Limpa tabelas no inicio de cada teste.
    Para SQLite: Usa banco em memoria (ja isolado por natureza).
    """
    if use_postgres:
        # PostgreSQL: Limpa tabelas antes de cada teste para isolamento
        async_session = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session() as session:
            # Limpa todas as tabelas antes do teste
            await _truncate_all_tables(session)
            yield session
            # Commit final para garantir que dados do teste persistem
            # (para testes manuais depois)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
    else:
        # SQLite em memoria: cada teste ja tem banco isolado
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


# -----------------------------------------------------------------------------
# Fixtures para testes de integracao (API)
# -----------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="function")
async def test_app(async_engine, use_postgres):
    """
    Cria aplicacao FastAPI configurada para testes.

    Para PostgreSQL: Limpa tabelas antes de cada teste para isolamento.
    Para SQLite: Usa banco em memoria (ja isolado por natureza).
    """
    from app.core.rate_limit import limiter
    from app.database import get_db
    from app.main import app

    # Reset rate limiter para cada teste
    limiter.reset()

    if use_postgres:
        # PostgreSQL: Limpa tabelas antes de cada teste
        async_session_factory = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Limpa tabelas antes do teste
        async with async_session_factory() as cleanup_session:
            await _truncate_all_tables(cleanup_session)

        # Override da dependencia de banco
        async def override_get_db():
            async with async_session_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

        app.dependency_overrides[get_db] = override_get_db

        yield app
    else:
        # SQLite em memoria: cada teste ja tem banco isolado
        async def override_get_db():
            async_session = sessionmaker(
                async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            async with async_session() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

        app.dependency_overrides[get_db] = override_get_db

        yield app

    # Limpa overrides apos testes
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(test_app) -> AsyncGenerator[Any, None]:
    """
    Cliente HTTP async para testar endpoints.

    Uso:
        async def test_endpoint(client):
            response = await client.get("/api/v1/users")
            assert response.status_code == 200
    """
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as ac:
        yield ac


# -----------------------------------------------------------------------------
# Fixtures de autenticacao para admin
# -----------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession):
    """Cria usuario admin para testes."""
    from app.core.security import get_password_hash
    from app.models.user import User, UserRole

    user = User(
        name="Admin Test",
        email="admin@test.com",
        password_hash=get_password_hash("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def editor_user(db_session: AsyncSession):
    """Cria usuario editor para testes."""
    from app.core.security import get_password_hash
    from app.models.user import User, UserRole

    user = User(
        name="Editor Test",
        email="editor@test.com",
        password_hash=get_password_hash("editorpassword123"),
        role=UserRole.EDITOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def admin_auth_cookie(admin_user) -> dict:
    """Cookie de autenticacao para admin."""
    from app.core.security import create_access_token

    token = create_access_token(
        subject=str(admin_user.id),
        extra_claims={"role": admin_user.role.value},
    )
    return {"admin_token": token}


@pytest.fixture
def editor_auth_cookie(editor_user) -> dict:
    """Cookie de autenticacao para editor."""
    from app.core.security import create_access_token

    token = create_access_token(
        subject=str(editor_user.id),
        extra_claims={"role": editor_user.role.value},
    )
    return {"admin_token": token}
