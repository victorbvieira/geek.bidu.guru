"""
Utilitarios para contexto de templates.

Fornece funcoes para buscar dados comuns usados em todos os templates,
como categorias do footer, configuracoes globais, etc.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category import CategoryRepository


async def get_footer_context(db: AsyncSession) -> dict[str, Any]:
    """
    Retorna contexto para o footer com categorias dinamicas.

    Busca ate 6 categorias raiz para exibir no footer.

    Args:
        db: Sessao do banco de dados

    Returns:
        Dicionario com footer_categories
    """
    category_repo = CategoryRepository(db)

    # Busca categorias raiz (sem parent) - limite de 6 para o footer
    categories = await category_repo.get_root_categories()

    return {
        "footer_categories": categories[:6],
    }


async def get_common_context(db: AsyncSession) -> dict[str, Any]:
    """
    Retorna contexto comum para todos os templates SSR.

    Inclui:
    - Categorias do footer
    - Outras configuracoes globais futuras

    Args:
        db: Sessao do banco de dados

    Returns:
        Dicionario com todo o contexto comum
    """
    footer = await get_footer_context(db)

    return {
        **footer,
    }
