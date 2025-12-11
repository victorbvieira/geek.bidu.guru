"""
Endpoints REST para gerenciamento de Produtos de Afiliados.

Este módulo implementa as operações CRUD para produtos de plataformas
de afiliados (Amazon, Mercado Livre, Shopee).

Endpoints disponíveis:
    GET    /products             - Lista produtos com paginação e filtros
    GET    /products/available   - Lista produtos disponíveis
    GET    /products/top-clicked - Lista mais clicados
    GET    /products/{id}        - Busca produto por ID
    GET    /products/slug/{s}    - Busca produto por slug
    POST   /products             - Cria novo produto
    PATCH  /products/{id}        - Atualiza produto existente
    PATCH  /products/{id}/price  - Atualiza apenas preço
    DELETE /products/{id}        - Remove produto

Plataformas de Afiliados:
    - amazon: Amazon Brasil
    - mercadolivre: Mercado Livre
    - shopee: Shopee Brasil

Faixas de Preço:
    - 0-50: Até R$ 50
    - 50-100: R$ 50 a R$ 100
    - 100-200: R$ 100 a R$ 200
    - 200+: Acima de R$ 200

Disponibilidade:
    - available: Produto disponível
    - unavailable: Produto indisponível
    - unknown: Status desconhecido

Métricas:
    - click_count: Contador de cliques no link de afiliado
    - internal_score: Score para curadoria de produtos

Protecao de Endpoints:
    Para proteger um endpoint, adicione a dependencia require_role ou ActiveUser:

    from app.core.deps import ActiveUser, require_role
    from app.models.user import UserRole

    # Qualquer usuario autenticado:
    @router.get("/protected")
    async def protected_route(current_user: ActiveUser):
        return {"user": current_user.email}

    # Admin, Editor ou Automation (criar/editar produtos):
    @router.post("", dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTOMATION))])
    async def create_product(...): ...

    # Apenas automation (atualizar precos via workflow):
    @router.patch("/{id}/price", dependencies=[Depends(require_role(UserRole.AUTOMATION, UserRole.ADMIN))])
    async def update_price(...): ...
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import Pagination, ProductRepo
from app.models.product import PriceRange, ProductPlatform
from app.schemas import (
    MessageResponse,
    PaginatedResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductUpdatePrice,
)

# Router com prefixo /products e tag para documentação OpenAPI
router = APIRouter(prefix="/products", tags=["products"])


# =============================================================================
# Endpoints de Leitura (GET)
# =============================================================================


@router.get("", response_model=PaginatedResponse)
async def list_products(
    repo: ProductRepo,
    pagination: Pagination,
    platform: ProductPlatform | None = None,
    price_range: PriceRange | None = None,
):
    """
    Lista produtos com paginação e filtros opcionais.

    Retorna todos os produtos independente de disponibilidade.
    Para listagem pública, use /available.

    Args:
        repo: Repositório de produtos (injetado automaticamente)
        pagination: Parâmetros de paginação
        platform: Filtrar por plataforma (amazon, mercadolivre, shopee)
        price_range: Filtrar por faixa de preço

    Returns:
        PaginatedResponse com lista de produtos

    Query Parameters:
        page (int): Número da página
        per_page (int): Itens por página
        platform (str): Filtro por plataforma (opcional)
        price_range (str): Filtro por faixa de preço (opcional)

    Exemplo:
        GET /products?platform=amazon&price_range=50-100
    """
    # Aplica filtro por plataforma se especificado
    if platform:
        products = await repo.get_by_platform(
            platform=platform,
            skip=pagination["skip"],
            limit=pagination["limit"],
        )
    else:
        # Sem filtro, retorna todos ordenados por data de criação
        products = await repo.get_multi(
            skip=pagination["skip"],
            limit=pagination["limit"],
            order_by="created_at",  # Mais recentes primeiro
        )

    total = await repo.count()

    return PaginatedResponse.create(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/available", response_model=PaginatedResponse)
async def list_available_products(
    repo: ProductRepo,
    pagination: Pagination,
    platform: ProductPlatform | None = None,
    price_range: PriceRange | None = None,
):
    """
    Lista produtos disponíveis (endpoint público para frontend).

    Retorna apenas produtos com availability='available'.
    Usado para exibição em posts e listagens públicas.

    Args:
        repo: Repositório de produtos (injetado automaticamente)
        pagination: Parâmetros de paginação
        platform: Filtrar por plataforma (opcional)
        price_range: Filtrar por faixa de preço (opcional)

    Returns:
        PaginatedResponse com lista de produtos disponíveis

    Uso típico:
        - Cards de produto em posts
        - Listagens de produtos por categoria
        - Seções de produtos relacionados
    """
    products = await repo.get_available(
        skip=pagination["skip"],
        limit=pagination["limit"],
        platform=platform,
        price_range=price_range,
    )
    total = await repo.count()

    return PaginatedResponse.create(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/top-clicked", response_model=list[ProductResponse])
async def list_top_clicked(
    repo: ProductRepo,
    limit: int = Query(10, ge=1, le=50),
):
    """
    Lista produtos mais clicados.

    Retorna produtos ordenados por click_count decrescente.
    Útil para seções de "mais populares" e análise de performance.

    Args:
        repo: Repositório de produtos (injetado automaticamente)
        limit: Número máximo de produtos a retornar (1-50)

    Returns:
        Lista de produtos ordenados por cliques

    Query Parameters:
        limit (int): Quantidade de produtos (default: 10, max: 50)

    Uso:
        - Seção "Mais Populares"
        - Dashboard administrativo
        - Relatórios de performance
    """
    products = await repo.get_top_clicked(limit=limit)
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, repo: ProductRepo):
    """
    Busca um produto específico por seu ID.

    Args:
        product_id: UUID do produto a ser buscado
        repo: Repositório de produtos (injetado automaticamente)

    Returns:
        ProductResponse com dados completos do produto

    Raises:
        HTTPException 404: Se o produto não for encontrado
    """
    product = await repo.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    return ProductResponse.model_validate(product)


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(slug: str, repo: ProductRepo):
    """
    Busca produto por slug (URL amigável).

    Usado para páginas de produto individuais onde o slug
    aparece na URL.

    Args:
        slug: Slug único do produto
        repo: Repositório de produtos (injetado automaticamente)

    Returns:
        ProductResponse com dados completos do produto

    Raises:
        HTTPException 404: Se o produto não for encontrado
    """
    product = await repo.get_by_slug(slug)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    return ProductResponse.model_validate(product)


# =============================================================================
# Endpoints de Escrita (POST, PATCH, DELETE)
# =============================================================================


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, repo: ProductRepo):
    """
    Cria um novo produto de afiliado.

    Requer slug único e affiliate_redirect_slug único para
    o sistema de redirect (/goto/{slug}).

    Args:
        data: Dados do produto a ser criado (ProductCreate schema)
        repo: Repositório de produtos (injetado automaticamente)

    Returns:
        ProductResponse com dados do produto criado

    Raises:
        HTTPException 400: Se o slug já existir
        HTTPException 400: Se o redirect_slug já existir

    Body (JSON):
        {
            "name": "Funko Pop Darth Vader",
            "slug": "funko-pop-darth-vader",
            "short_description": "Boneco colecionável",
            "price": 149.90,
            "affiliate_url_raw": "https://amazon.com.br/...",
            "affiliate_redirect_slug": "funko-vader",
            "platform": "amazon",
            "availability": "available"
        }
    """
    # Valida unicidade do slug principal
    if await repo.slug_exists(data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    # Valida unicidade do redirect slug (usado em /goto/{slug})
    if await repo.redirect_slug_exists(data.affiliate_redirect_slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Redirect slug ja existe",
        )

    product = await repo.create(data.model_dump())
    return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, data: ProductUpdate, repo: ProductRepo):
    """
    Atualiza um produto existente (atualização parcial).

    Permite atualizar qualquer campo do produto.
    Para atualizar apenas preço, use /products/{id}/price.

    Args:
        product_id: UUID do produto a ser atualizado
        data: Campos a serem atualizados (ProductUpdate schema)
        repo: Repositório de produtos (injetado automaticamente)

    Returns:
        ProductResponse com dados atualizados

    Raises:
        HTTPException 404: Se o produto não for encontrado
        HTTPException 400: Se o novo slug já existir
    """
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Se está alterando slug, verifica duplicação
    if data.slug and await repo.slug_exists(data.slug, exclude_id=product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    update_data = data.model_dump(exclude_unset=True)
    product = await repo.update(product, update_data)
    return ProductResponse.model_validate(product)


@router.patch("/{product_id}/price", response_model=ProductResponse)
async def update_product_price(
    product_id: UUID, data: ProductUpdatePrice, repo: ProductRepo
):
    """
    Atualiza apenas o preço do produto.

    Endpoint específico para atualização de preços, útil para
    workflows de automação (n8n) que sincronizam preços.

    Args:
        product_id: UUID do produto a ser atualizado
        data: Novo preço e campos relacionados
        repo: Repositório de produtos (injetado automaticamente)

    Returns:
        ProductResponse com preço atualizado

    Raises:
        HTTPException 404: Se o produto não for encontrado

    Body (JSON):
        {
            "price": 129.90,
            "availability": "available"  // opcional
        }

    Uso típico:
        - Workflow n8n de atualização de preços
        - Sincronização com APIs das plataformas
        - Atualização em massa via script
    """
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    update_data = data.model_dump(exclude_unset=True)
    product = await repo.update(product, update_data)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(product_id: UUID, repo: ProductRepo):
    """
    Remove um produto do sistema.

    Atenção: Links de afiliado (/goto/) para este produto
    deixarão de funcionar após a remoção.

    Args:
        product_id: UUID do produto a ser removido
        repo: Repositório de produtos (injetado automaticamente)

    Returns:
        MessageResponse confirmando a remoção

    Raises:
        HTTPException 404: Se o produto não for encontrado

    Cuidados:
        - Links em posts ficarão quebrados
        - Histórico de cliques será perdido
        - Considerar availability=unavailable em vez de deletar
    """
    if not await repo.exists(product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    await repo.delete(product_id)
    return MessageResponse(message="Produto removido com sucesso")
