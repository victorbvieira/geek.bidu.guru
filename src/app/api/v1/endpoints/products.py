"""
Endpoints REST para gerenciamento de Produtos de Afiliados.

Este módulo implementa as operações CRUD para produtos de plataformas
de afiliados (Amazon, Mercado Livre, Shopee).

Endpoints disponíveis:
    GET    /products                                      - Lista produtos com paginação e filtros
    GET    /products/available                            - Lista produtos disponíveis
    GET    /products/top-clicked                          - Lista mais clicados
    GET    /products/{id}                                 - Busca produto por ID
    GET    /products/slug/{s}                             - Busca produto por slug
    POST   /products                                      - Cria novo produto
    PATCH  /products/{id}                                 - Atualiza produto existente
    PATCH  /products/{id}/price                           - Atualiza apenas preço
    PATCH  /products/{id}/instagram-metadata              - Atualiza metadados Instagram + custo LLM
    PATCH  /products/platform/{platform}/{platform_id}    - Atualiza por plataforma/ID externo
    DELETE /products/{id}                                 - Remove produto

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

from fastapi import APIRouter, Depends, HTTPException, Query, status

from datetime import datetime, UTC

from app.api.deps import Pagination, PriceHistoryRepo, ProductRepo
from app.core.deps import require_role
from app.models.product import PriceRange, ProductPlatform, ProductStatus
from app.models.user import UserRole
from app.schemas import (
    MessageResponse,
    PaginatedResponse,
    ProductCreate,
    ProductPlatformUpdate,
    ProductPlatformUpdateResponse,
    ProductResponse,
    ProductUpdate,
    ProductUpdatePrice,
)
from app.schemas.instagram import (
    InstagramMetadataUpdate,
    InstagramMetadataUpdateResponse,
)
from app.schemas.product import PUBLISH_REQUIRES_AFFILIATE_MSG, is_publishable

# Router com prefixo /products e tag para documentação OpenAPI
router = APIRouter(prefix="/products", tags=["products"])

# Roles permitidos para operações de escrita (criar, editar, deletar)
WRITE_ROLES = [UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTOMATION]


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


# =============================================================================
# Endpoints de Atualizacao por Plataforma (para integracao com APIs externas)
# IMPORTANTE: Este endpoint deve vir ANTES dos endpoints com {product_id}
# para evitar conflito de rotas no FastAPI
# =============================================================================


@router.patch(
    "/platform/{platform}/{platform_product_id}",
    response_model=ProductPlatformUpdateResponse,
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.AUTOMATION))],
)
async def update_product_by_platform(
    platform: ProductPlatform,
    platform_product_id: str,
    data: ProductPlatformUpdate,
    product_repo: ProductRepo,
    price_history_repo: PriceHistoryRepo,
):
    """
    Atualiza produto identificado por plataforma e ID do produto na plataforma.

    **Autenticação**: Requer token JWT com role ADMIN ou AUTOMATION.

    Este endpoint e projetado para integracao com workflows n8n e APIs externas
    que precisam atualizar produtos usando o identificador da plataforma
    (ex: ASIN da Amazon, MLB do Mercado Livre) em vez do UUID interno.

    **Historico de Precos**:
    Se o campo `price` for enviado e for diferente do preco atual, um novo
    registro sera criado automaticamente no historico de precos com:
    - Preco anterior
    - Novo preco
    - Fonte da atualizacao (campo `source`)
    - Observacoes (campo `notes`)

    Args:
        platform: Plataforma do produto (amazon, mercadolivre, shopee)
        platform_product_id: ID do produto na plataforma (ex: B08N5WRWNW)
        data: Campos a serem atualizados (ProductPlatformUpdate schema)
        product_repo: Repositório de produtos (injetado automaticamente)
        price_history_repo: Repositório de histórico de preços (injetado automaticamente)

    Returns:
        ProductPlatformUpdateResponse com informacoes da atualizacao

    Raises:
        HTTPException 404: Se o produto nao for encontrado

    Path Parameters:
        platform (str): Plataforma (amazon, mercadolivre, shopee)
        platform_product_id (str): ID do produto na plataforma

    Body (JSON):
        {
            "price": 129.90,
            "availability": "available",
            "status": "published",
            "rating": 4.5,
            "review_count": 1250,
            "amazon_clean_url": "https://www.amazon.com.br/dp/B08N5WRWNW",
            "internal_notes": "Cadastrado pelo agente de IA - revisar link de afiliado",
            "source": "api_amazon",
            "notes": "Atualizacao automatica via PA-API"
        }

    Exemplo de uso (cURL):
        curl -X PATCH "https://geek.bidu.guru/api/v1/products/platform/amazon/B08N5WRWNW" \\
            -H "Authorization: Bearer {token}" \\
            -H "Content-Type: application/json" \\
            -d '{"price": 129.90, "availability": "available"}'

    Exemplo n8n:
        - HTTP Request node
        - Method: PATCH
        - URL: /api/v1/products/platform/{{ $json.platform }}/{{ $json.asin }}
        - Body: { "price": {{ $json.price }}, "availability": "available" }
    """
    # Busca o produto pela combinacao plataforma + ID
    product = await product_repo.get_by_platform_product_id(
        platform=platform,
        platform_product_id=platform_product_id,
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto nao encontrado: {platform.value}/{platform_product_id}",
        )

    # Extrai os campos que serao atualizados (ignora source e notes que sao para historico)
    update_data = data.model_dump(exclude_unset=True, exclude={"source", "notes"})
    updated_fields = list(update_data.keys())

    # Regra: produto so pode ficar publicado se tiver URL de afiliado.
    result_status = update_data.get("status", product.status)
    result_affiliate = update_data.get("affiliate_url_raw", product.affiliate_url_raw)
    if not is_publishable(result_status, result_affiliate):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PUBLISH_REQUIRES_AFFILIATE_MSG,
        )

    # Variaveis para resposta
    price_history_created = False
    previous_price = None
    new_price = None

    # Se o preco esta sendo atualizado, registra no historico
    if "price" in update_data and update_data["price"] is not None:
        new_price = update_data["price"]

        # Verifica se o preco realmente mudou
        if product.price is None or product.price != new_price:
            previous_price = product.price

            # Cria registro no historico de precos
            await price_history_repo.create_price_record(
                product_id=product.id,
                price=new_price,
                previous_price=previous_price,
                source=data.source,
                notes=data.notes,
            )
            price_history_created = True

            # Atualiza last_price_update no produto
            update_data["last_price_update"] = datetime.now(UTC)

    # Se price_range nao foi fornecido mas o preco foi atualizado,
    # calcula automaticamente o price_range
    if "price" in update_data and "price_range" not in update_data:
        price = update_data["price"]
        if price is not None:
            if price < 50:
                update_data["price_range"] = PriceRange.RANGE_0_50
            elif price < 100:
                update_data["price_range"] = PriceRange.RANGE_50_100
            elif price < 200:
                update_data["price_range"] = PriceRange.RANGE_100_200
            else:
                update_data["price_range"] = PriceRange.RANGE_200_PLUS

    # Atualiza o produto
    if update_data:
        product = await product_repo.update(product, update_data)

    return ProductPlatformUpdateResponse(
        success=True,
        product_id=product.id,
        platform=platform,
        platform_product_id=platform_product_id,
        updated_fields=updated_fields,
        price_history_created=price_history_created,
        previous_price=previous_price,
        new_price=new_price,
        availability=product.availability,
    )


# =============================================================================
# Endpoints com {product_id} - DEVEM vir DEPOIS dos endpoints com paths fixos
# =============================================================================


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
async def get_product_by_slug(
    slug: str,
    repo: ProductRepo,
    status_filter: ProductStatus | None = Query(
        None,
        alias="status",
        description=(
            "Filtra por status de publicacao (draft, published, unpublished). "
            "Se omitido, retorna apenas produtos publicados."
        ),
    ),
):
    """
    Busca produto por slug (URL amigável).

    Usado para páginas de produto individuais onde o slug
    aparece na URL.

    Por padrão retorna apenas produtos **publicados**. Para buscar produtos
    em outro status, informe o parâmetro `status` (draft, unpublished).

    Args:
        slug: Slug único do produto
        repo: Repositório de produtos (injetado automaticamente)
        status_filter: Status de publicacao (opcional; default = published)

    Returns:
        ProductResponse com dados completos do produto

    Raises:
        HTTPException 404: Se o produto não for encontrado
    """
    # Sem status informado -> default do repositorio (published)
    if status_filter is None:
        product = await repo.get_by_slug(slug)
    else:
        product = await repo.get_by_slug(slug, status=status_filter)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    return ProductResponse.model_validate(product)


# =============================================================================
# Endpoints de Escrita (POST, PATCH, DELETE)
# =============================================================================


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*WRITE_ROLES))],
)
async def create_product(data: ProductCreate, repo: ProductRepo):
    """
    Cria um novo produto de afiliado.

    **Autenticação**: Requer token JWT com role ADMIN, EDITOR ou AUTOMATION.

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


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_role(*WRITE_ROLES))],
)
async def update_product(product_id: UUID, data: ProductUpdate, repo: ProductRepo):
    """
    Atualiza um produto existente (atualização parcial).

    **Autenticação**: Requer token JWT com role ADMIN, EDITOR ou AUTOMATION.

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

    # Regra: produto so pode ficar publicado se tiver URL de afiliado.
    # Avalia o estado resultante (valor novo, ou o atual se nao for alterado).
    result_status = update_data.get("status", product.status)
    result_affiliate = update_data.get("affiliate_url_raw", product.affiliate_url_raw)
    if not is_publishable(result_status, result_affiliate):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PUBLISH_REQUIRES_AFFILIATE_MSG,
        )

    product = await repo.update(product, update_data)
    return ProductResponse.model_validate(product)


@router.patch(
    "/{product_id}/price",
    response_model=ProductResponse,
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.AUTOMATION))],
)
async def update_product_price(
    product_id: UUID, data: ProductUpdatePrice, repo: ProductRepo
):
    """
    Atualiza apenas o preço do produto.

    **Autenticação**: Requer token JWT com role ADMIN ou AUTOMATION.

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


@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def delete_product(product_id: UUID, repo: ProductRepo):
    """
    Remove um produto do sistema.

    **Autenticação**: Requer token JWT com role ADMIN.

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


# =============================================================================
# Endpoints de Metadados Instagram
# =============================================================================


@router.patch(
    "/{product_id}/instagram-metadata",
    response_model=InstagramMetadataUpdateResponse,
    dependencies=[Depends(require_role(*WRITE_ROLES))],
)
async def update_instagram_metadata(
    product_id: UUID,
    data: InstagramMetadataUpdate,
    repo: ProductRepo,
):
    """
    Atualiza metadados de Instagram de um produto.

    **Autenticação**: Requer token JWT com role ADMIN, EDITOR ou AUTOMATION.

    Este endpoint e usado pelo workflow n8n para salvar dados gerados
    por IA (headline, title, badge, caption, hashtags) e registrar
    o custo da geracao.

    Campos atualizaveis:
    - instagram_headline: Headline de impacto (max 40 chars)
    - instagram_title: Titulo para imagem (max 100 chars)
    - instagram_badge: Texto do badge (max 20 chars)
    - instagram_caption: Caption do post (max 2200 chars)
    - instagram_hashtags: Lista de hashtags (sem #)

    Custo LLM (opcional):
    Se o campo llm_cost for enviado, atualiza as metricas de IA do produto:
    - ai_tokens_used: soma de input + output tokens
    - ai_prompt_tokens: tokens de entrada
    - ai_completion_tokens: tokens de saida
    - ai_cost_usd: custo em USD (acumulado)
    - ai_generations_count: incrementa contador

    Args:
        product_id: UUID do produto a ser atualizado
        data: Metadados Instagram e info de custo LLM (opcional)
        repo: Repositório de produtos (injetado automaticamente)

    Returns:
        InstagramMetadataUpdateResponse com campos atualizados

    Raises:
        HTTPException 404: Se o produto não for encontrado

    Body (JSON):
        {
            "instagram_headline": "DESPERTE SEU HEROI!",
            "instagram_title": "Material Escolar Epico e Aqui!",
            "instagram_badge": "NOVO NA LOJA!",
            "instagram_caption": "🦸 Comece o ano letivo com estilo...",
            "instagram_hashtags": ["Vingadores", "Marvel", "GeekGeek"],
            "llm_cost": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "input_tokens": 250,
                "output_tokens": 180,
                "cost_usd": 0.00043
            }
        }
    """
    # Busca o produto
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Prepara campos de Instagram para atualizacao (exclui llm_cost)
    update_data = data.model_dump(exclude_unset=True, exclude={"llm_cost"})
    updated_fields = list(update_data.keys())

    # Processa informacoes de custo LLM se fornecidas
    llm_cost_registered = False
    if data.llm_cost:
        llm_cost = data.llm_cost
        total_tokens = llm_cost.input_tokens + llm_cost.output_tokens

        # Acumula os custos de IA no produto
        update_data["ai_tokens_used"] = product.ai_tokens_used + total_tokens
        update_data["ai_prompt_tokens"] = product.ai_prompt_tokens + llm_cost.input_tokens
        update_data["ai_completion_tokens"] = product.ai_completion_tokens + llm_cost.output_tokens
        update_data["ai_cost_usd"] = float(product.ai_cost_usd) + llm_cost.cost_usd
        update_data["ai_generations_count"] = product.ai_generations_count + 1

        llm_cost_registered = True

    # Atualiza o produto
    product = await repo.update(product, update_data)

    return InstagramMetadataUpdateResponse(
        success=True,
        product_id=product.id,
        updated_fields=updated_fields,
        llm_cost_registered=llm_cost_registered,
        total_llm_cost_usd=float(product.ai_cost_usd) if llm_cost_registered else None,
    )
