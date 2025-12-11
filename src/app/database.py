"""
Configuracao do banco de dados PostgreSQL com SQLAlchemy async.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# -----------------------------------------------------------------------------
# Engine e Session
# -----------------------------------------------------------------------------

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL em desenvolvimento
    pool_pre_ping=True,  # Verifica conexao antes de usar
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# -----------------------------------------------------------------------------
# Base para modelos
# -----------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""

    pass


# -----------------------------------------------------------------------------
# Dependency para FastAPI
# -----------------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que fornece uma sessao do banco de dados.

    Uso:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# -----------------------------------------------------------------------------
# Funcoes utilitarias
# -----------------------------------------------------------------------------


async def check_database_connection() -> bool:
    """Verifica se a conexao com o banco esta funcionando."""
    from sqlalchemy import text

    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
