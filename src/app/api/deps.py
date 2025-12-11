"""
Dependencias compartilhadas para endpoints da API.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories import (
    CategoryRepository,
    ClickRepository,
    NewsletterRepository,
    PostRepository,
    ProductRepository,
    SessionRepository,
    UserRepository,
)

# Type alias para injeção de dependência
DBSession = Annotated[AsyncSession, Depends(get_db)]


# -----------------------------------------------------------------------------
# Repositorios como dependencias
# -----------------------------------------------------------------------------


async def get_user_repo(db: DBSession) -> UserRepository:
    """Retorna repositorio de usuarios."""
    return UserRepository(db)


async def get_category_repo(db: DBSession) -> CategoryRepository:
    """Retorna repositorio de categorias."""
    return CategoryRepository(db)


async def get_post_repo(db: DBSession) -> PostRepository:
    """Retorna repositorio de posts."""
    return PostRepository(db)


async def get_product_repo(db: DBSession) -> ProductRepository:
    """Retorna repositorio de produtos."""
    return ProductRepository(db)


async def get_click_repo(db: DBSession) -> ClickRepository:
    """Retorna repositorio de cliques."""
    return ClickRepository(db)


async def get_session_repo(db: DBSession) -> SessionRepository:
    """Retorna repositorio de sessoes."""
    return SessionRepository(db)


async def get_newsletter_repo(db: DBSession) -> NewsletterRepository:
    """Retorna repositorio de newsletter."""
    return NewsletterRepository(db)


# Type aliases para injecao
UserRepo = Annotated[UserRepository, Depends(get_user_repo)]
CategoryRepo = Annotated[CategoryRepository, Depends(get_category_repo)]
PostRepo = Annotated[PostRepository, Depends(get_post_repo)]
ProductRepo = Annotated[ProductRepository, Depends(get_product_repo)]
ClickRepo = Annotated[ClickRepository, Depends(get_click_repo)]
SessionRepo = Annotated[SessionRepository, Depends(get_session_repo)]
NewsletterRepo = Annotated[NewsletterRepository, Depends(get_newsletter_repo)]


# -----------------------------------------------------------------------------
# Paginacao
# -----------------------------------------------------------------------------


def pagination_params(
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """Parametros de paginacao padrao."""
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 1
    if per_page > 100:
        per_page = 100

    return {
        "skip": (page - 1) * per_page,
        "limit": per_page,
        "page": page,
        "per_page": per_page,
    }


Pagination = Annotated[dict, Depends(pagination_params)]
