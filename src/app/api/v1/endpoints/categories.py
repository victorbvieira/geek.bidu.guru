"""
Endpoints REST para gerenciamento de Categorias.

Este módulo implementa as operações CRUD para categorias do blog,
incluindo suporte a hierarquia (categorias pai/filho).

Endpoints disponíveis:
    GET    /categories           - Lista todas as categorias com paginação
    GET    /categories/root      - Lista apenas categorias raiz (sem pai)
    GET    /categories/{id}      - Busca categoria por ID
    GET    /categories/slug/{s}  - Busca categoria por slug
    GET    /categories/{id}/children - Lista subcategorias
    POST   /categories           - Cria nova categoria
    PATCH  /categories/{id}      - Atualiza categoria existente
    DELETE /categories/{id}      - Remove categoria

Hierarquia de Categorias:
    - Categorias podem ter um parent_id opcional
    - Categorias sem parent_id são consideradas "raiz"
    - Permite navegação por árvore de categorias

Validações:
    - Slugs devem ser únicos
    - Parent_id deve referenciar categoria existente
    - Categoria não pode ser pai de si mesma
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CategoryRepo, Pagination
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    MessageResponse,
    PaginatedResponse,
)

# Router com prefixo /categories e tag para documentação OpenAPI
router = APIRouter(prefix="/categories", tags=["categories"])


# =============================================================================
# Endpoints de Leitura (GET)
# =============================================================================


@router.get("", response_model=PaginatedResponse)
async def list_categories(
    repo: CategoryRepo,
    pagination: Pagination,
):
    """
    Lista todas as categorias com paginação.

    Retorna categorias ordenadas alfabeticamente por nome.

    Args:
        repo: Repositório de categorias (injetado automaticamente)
        pagination: Parâmetros de paginação da query string

    Returns:
        PaginatedResponse com lista de categorias

    Query Parameters:
        page (int): Número da página (default: 1)
        per_page (int): Itens por página (default: 20, max: 100)
    """
    # Busca categorias ordenadas por nome (A-Z)
    categories = await repo.get_multi(
        skip=pagination["skip"],
        limit=pagination["limit"],
        order_by="name",
        desc=False,  # Ordem alfabética ascendente
    )
    total = await repo.count()

    return PaginatedResponse.create(
        items=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/root", response_model=list[CategoryResponse])
async def list_root_categories(repo: CategoryRepo):
    """
    Lista apenas categorias raiz (sem parent).

    Útil para construir menus de navegação e árvores de categorias.
    Categorias raiz são o primeiro nível da hierarquia.

    Args:
        repo: Repositório de categorias (injetado automaticamente)

    Returns:
        Lista de categorias sem parent_id

    Exemplo de uso:
        - Menu principal do site
        - Breadcrumb navigation
        - Sidebar de categorias
    """
    categories = await repo.get_root_categories()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID, repo: CategoryRepo):
    """
    Busca uma categoria específica por seu ID.

    Args:
        category_id: UUID da categoria a ser buscada
        repo: Repositório de categorias (injetado automaticamente)

    Returns:
        CategoryResponse com dados da categoria

    Raises:
        HTTPException 404: Se a categoria não for encontrada
    """
    category = await repo.get(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    return CategoryResponse.model_validate(category)


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(slug: str, repo: CategoryRepo):
    """
    Busca categoria por slug (URL amigável).

    Usado principalmente para rotas SSR do frontend onde o slug
    aparece na URL (ex: /categoria/funko-pop).

    Args:
        slug: Slug único da categoria
        repo: Repositório de categorias (injetado automaticamente)

    Returns:
        CategoryResponse com dados da categoria

    Raises:
        HTTPException 404: Se a categoria não for encontrada
    """
    category = await repo.get_by_slug(slug)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    return CategoryResponse.model_validate(category)


@router.get("/{category_id}/children", response_model=list[CategoryResponse])
async def list_subcategories(category_id: UUID, repo: CategoryRepo):
    """
    Lista subcategorias (filhas) de uma categoria.

    Retorna todas as categorias que têm parent_id igual ao ID fornecido.
    Útil para navegação hierárquica e menus em cascata.

    Args:
        category_id: UUID da categoria pai
        repo: Repositório de categorias (injetado automaticamente)

    Returns:
        Lista de categorias filhas

    Raises:
        HTTPException 404: Se a categoria pai não for encontrada

    Exemplo:
        GET /categories/123/children
        Retorna todas as subcategorias de "Colecionáveis"
    """
    # Verifica se categoria pai existe
    if not await repo.exists(category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    children = await repo.get_children(category_id)
    return [CategoryResponse.model_validate(c) for c in children]


# =============================================================================
# Endpoints de Escrita (POST, PATCH, DELETE)
# =============================================================================


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, repo: CategoryRepo):
    """
    Cria uma nova categoria.

    O slug deve ser único no sistema. Opcionalmente pode ter uma
    categoria pai para criar hierarquias.

    Args:
        data: Dados da categoria a ser criada (CategoryCreate schema)
        repo: Repositório de categorias (injetado automaticamente)

    Returns:
        CategoryResponse com dados da categoria criada

    Raises:
        HTTPException 400: Se o slug já existir
        HTTPException 400: Se o parent_id não existir

    Body (JSON):
        {
            "name": "Funko Pop",
            "slug": "funko-pop",
            "description": "Bonecos colecionáveis",
            "parent_id": null  // opcional
        }
    """
    # Valida unicidade do slug
    if await repo.slug_exists(data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    # Se tem parent_id, verifica se a categoria pai existe
    if data.parent_id and not await repo.exists(data.parent_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categoria pai nao encontrada",
        )

    # Cria e retorna categoria
    category = await repo.create(data.model_dump())
    return CategoryResponse.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID, data: CategoryUpdate, repo: CategoryRepo
):
    """
    Atualiza uma categoria existente (atualização parcial).

    Permite atualizar nome, slug, descrição e categoria pai.
    Valida unicidade do slug e integridade da hierarquia.

    Args:
        category_id: UUID da categoria a ser atualizada
        data: Campos a serem atualizados (CategoryUpdate schema)
        repo: Repositório de categorias (injetado automaticamente)

    Returns:
        CategoryResponse com dados atualizados

    Raises:
        HTTPException 404: Se a categoria não for encontrada
        HTTPException 400: Se o novo slug já existir
        HTTPException 400: Se tentar definir a própria categoria como pai
        HTTPException 400: Se o parent_id não existir
    """
    # Busca categoria existente
    category = await repo.get(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    # Se está alterando slug, verifica duplicação (excluindo a própria categoria)
    if data.slug and await repo.slug_exists(data.slug, exclude_id=category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    # Validações de hierarquia para parent_id
    if data.parent_id:
        # Não pode ser pai de si mesma (criaria ciclo)
        if data.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria nao pode ser pai de si mesma",
            )

        # Parent deve existir
        if not await repo.exists(data.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria pai nao encontrada",
            )

    # Atualiza apenas campos enviados
    update_data = data.model_dump(exclude_unset=True)
    category = await repo.update(category, update_data)
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(category_id: UUID, repo: CategoryRepo):
    """
    Remove uma categoria do sistema.

    Atenção: A remoção pode afetar posts e subcategorias associadas.
    Posts da categoria terão category_id definido como NULL.

    Args:
        category_id: UUID da categoria a ser removida
        repo: Repositório de categorias (injetado automaticamente)

    Returns:
        MessageResponse confirmando a remoção

    Raises:
        HTTPException 404: Se a categoria não for encontrada

    Cuidados:
        - Subcategorias órfãs terão parent_id = NULL
        - Posts da categoria ficarão sem categoria
        - Considerar soft delete em produção
    """
    # Verifica existência antes de deletar
    if not await repo.exists(category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    await repo.delete(category_id)
    return MessageResponse(message="Categoria removida com sucesso")
