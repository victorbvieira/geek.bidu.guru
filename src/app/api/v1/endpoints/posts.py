"""
Endpoints REST para gerenciamento de Posts (Artigos).

Este módulo implementa as operações CRUD para posts do blog,
incluindo suporte a workflow editorial (draft, review, published, etc).

Endpoints disponíveis:
    GET    /posts              - Lista posts com paginação e filtros
    GET    /posts/published    - Lista posts publicados (público)
    GET    /posts/{id}         - Busca post por ID
    GET    /posts/slug/{s}     - Busca post por slug
    POST   /posts              - Cria novo post
    PATCH  /posts/{id}         - Atualiza post existente
    PATCH  /posts/{id}/status  - Atualiza status do post
    POST   /posts/{id}/view    - Incrementa contador de views
    DELETE /posts/{id}         - Remove post

Tipos de Post:
    - product_single: Post sobre um único produto
    - listicle: Lista de produtos (Top 10, etc.)
    - guide: Guia de compra

Status de Post (Workflow Editorial):
    - draft: Rascunho (em edição)
    - review: Em revisão
    - scheduled: Agendado para publicação
    - published: Publicado
    - archived: Arquivado

Métricas:
    - view_count: Contador de visualizações
    - click_count: Contador de cliques em links de afiliados
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import Pagination, PostRepo
from app.models.post import PostStatus, PostType
from app.schemas import (
    MessageResponse,
    PaginatedResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
    PostUpdateStatus,
)

# Router com prefixo /posts e tag para documentação OpenAPI
router = APIRouter(prefix="/posts", tags=["posts"])


# =============================================================================
# Endpoints de Leitura (GET)
# =============================================================================


@router.get("", response_model=PaginatedResponse)
async def list_posts(
    repo: PostRepo,
    pagination: Pagination,
    status_filter: PostStatus | None = Query(None, alias="status"),
    type_filter: PostType | None = Query(None, alias="type"),
):
    """
    Lista posts com paginação e filtros opcionais.

    Endpoint administrativo que retorna posts de qualquer status.
    Para listagem pública, use /published.

    Args:
        repo: Repositório de posts (injetado automaticamente)
        pagination: Parâmetros de paginação
        status_filter: Filtrar por status (draft, review, published, etc.)
        type_filter: Filtrar por tipo (product_single, listicle, guide)

    Returns:
        PaginatedResponse com lista de posts

    Query Parameters:
        page (int): Número da página
        per_page (int): Itens por página
        status (str): Filtro por status (opcional)
        type (str): Filtro por tipo (opcional)

    Exemplo:
        GET /posts?status=draft&page=1&per_page=20
    """
    # Aplica filtro por status se especificado
    if status_filter:
        posts = await repo.get_by_status(
            status=status_filter,
            skip=pagination["skip"],
            limit=pagination["limit"],
        )
    else:
        # Sem filtro, retorna todos ordenados por data de criação
        posts = await repo.get_multi(
            skip=pagination["skip"],
            limit=pagination["limit"],
            order_by="created_at",  # Mais recentes primeiro
        )

    total = await repo.count()

    return PaginatedResponse.create(
        items=[PostResponse.model_validate(p) for p in posts],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/published", response_model=PaginatedResponse)
async def list_published_posts(
    repo: PostRepo,
    pagination: Pagination,
    category_id: UUID | None = None,
    post_type: PostType | None = Query(None, alias="type"),
):
    """
    Lista posts publicados (endpoint público para frontend).

    Retorna apenas posts com status=published e data de publicação
    já passada. Usado para renderização do blog público.

    Args:
        repo: Repositório de posts (injetado automaticamente)
        pagination: Parâmetros de paginação
        category_id: Filtrar por categoria (opcional)
        post_type: Filtrar por tipo de post (opcional)

    Returns:
        PaginatedResponse com lista de posts publicados

    Query Parameters:
        page (int): Número da página
        per_page (int): Itens por página
        category_id (UUID): Filtrar por categoria
        type (str): Filtrar por tipo de post

    Uso típico:
        - Homepage do blog
        - Página de categoria
        - Feed de posts
    """
    # Busca apenas posts publicados com filtros opcionais
    posts = await repo.get_published(
        skip=pagination["skip"],
        limit=pagination["limit"],
        category_id=category_id,
        post_type=post_type,
    )

    # Conta total de posts publicados com mesmos filtros
    total = await repo.count_published(category_id=category_id, post_type=post_type)

    return PaginatedResponse.create(
        items=[PostResponse.model_validate(p) for p in posts],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID, repo: PostRepo):
    """
    Busca um post específico por seu ID.

    Retorna o post com todos os relacionamentos carregados
    (categoria, autor, produtos).

    Args:
        post_id: UUID do post a ser buscado
        repo: Repositório de posts (injetado automaticamente)

    Returns:
        PostResponse com dados completos do post

    Raises:
        HTTPException 404: Se o post não for encontrado
    """
    # Usa método que carrega relacionamentos (categoria, autor)
    post = await repo.get_with_relations(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    return PostResponse.model_validate(post)


@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(slug: str, repo: PostRepo):
    """
    Busca post por slug (URL amigável).

    Usado para rotas SSR onde o slug aparece na URL
    (ex: /blog/top-10-presentes-geek).

    Args:
        slug: Slug único do post
        repo: Repositório de posts (injetado automaticamente)

    Returns:
        PostResponse com dados completos do post

    Raises:
        HTTPException 404: Se o post não for encontrado

    Nota:
        Usado pelo frontend para renderizar páginas de post
    """
    post = await repo.get_by_slug(slug)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    return PostResponse.model_validate(post)


# =============================================================================
# Endpoints de Escrita (POST, PATCH, DELETE)
# =============================================================================


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, repo: PostRepo):
    """
    Cria um novo post.

    Posts são criados com status "draft" por padrão.
    O slug deve ser único no sistema.

    Args:
        data: Dados do post a ser criado (PostCreate schema)
        repo: Repositório de posts (injetado automaticamente)

    Returns:
        PostResponse com dados do post criado

    Raises:
        HTTPException 400: Se o slug já existir

    Body (JSON):
        {
            "type": "listicle",
            "title": "Top 10 Produtos Geek",
            "slug": "top-10-produtos-geek",
            "content": "<p>Conteúdo HTML</p>",
            "category_id": "uuid...",  // opcional
            "tags": ["geek", "presentes"],
            "seo_title": "Top 10 Produtos",  // max 60 chars
            "seo_description": "Descubra..."  // max 160 chars
        }
    """
    # Valida unicidade do slug
    if await repo.slug_exists(data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    post = await repo.create(data.model_dump())
    return PostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: UUID, data: PostUpdate, repo: PostRepo):
    """
    Atualiza um post existente (atualização parcial).

    Permite atualizar qualquer campo do post exceto status
    (use /posts/{id}/status para isso).

    Args:
        post_id: UUID do post a ser atualizado
        data: Campos a serem atualizados (PostUpdate schema)
        repo: Repositório de posts (injetado automaticamente)

    Returns:
        PostResponse com dados atualizados

    Raises:
        HTTPException 404: Se o post não for encontrado
        HTTPException 400: Se o novo slug já existir
    """
    post = await repo.get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    # Se está alterando slug, verifica duplicação
    if data.slug and await repo.slug_exists(data.slug, exclude_id=post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    # Atualiza apenas campos enviados
    update_data = data.model_dump(exclude_unset=True)
    post = await repo.update(post, update_data)
    return PostResponse.model_validate(post)


@router.patch("/{post_id}/status", response_model=PostResponse)
async def update_post_status(
    post_id: UUID, data: PostUpdateStatus, repo: PostRepo
):
    """
    Atualiza o status do post (workflow editorial).

    Endpoint específico para transições de status:
    draft -> review -> scheduled/published -> archived

    Args:
        post_id: UUID do post a ser atualizado
        data: Novo status e data de publicação opcional
        repo: Repositório de posts (injetado automaticamente)

    Returns:
        PostResponse com status atualizado

    Raises:
        HTTPException 404: Se o post não for encontrado

    Body (JSON):
        {
            "status": "published",
            "publish_at": "2024-01-01T00:00:00Z"  // opcional
        }

    Fluxo típico:
        1. Autor cria (draft)
        2. Envia para revisão (review)
        3. Editor aprova e publica (published)
    """
    post = await repo.get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    update_data = data.model_dump(exclude_unset=True)
    post = await repo.update(post, update_data)
    return PostResponse.model_validate(post)


@router.post("/{post_id}/view", response_model=MessageResponse)
async def increment_view(post_id: UUID, repo: PostRepo):
    """
    Incrementa o contador de views do post.

    Chamado pelo frontend a cada visualização única de post.
    O controle de unicidade (sessão/IP) deve ser feito no frontend.

    Args:
        post_id: UUID do post visualizado
        repo: Repositório de posts (injetado automaticamente)

    Returns:
        MessageResponse confirmando o registro

    Raises:
        HTTPException 404: Se o post não for encontrado

    Uso:
        - Chamado via JavaScript após carregamento da página
        - Usado para métricas de popularidade
        - Base para relatórios de analytics
    """
    if not await repo.exists(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    await repo.increment_view_count(post_id)
    return MessageResponse(message="View registrada")


@router.delete("/{post_id}", response_model=MessageResponse)
async def delete_post(post_id: UUID, repo: PostRepo):
    """
    Remove um post do sistema.

    Realiza hard delete (remoção física). Para arquivar um post,
    use PATCH /posts/{id}/status com status="archived".

    Args:
        post_id: UUID do post a ser removido
        repo: Repositório de posts (injetado automaticamente)

    Returns:
        MessageResponse confirmando a remoção

    Raises:
        HTTPException 404: Se o post não for encontrado

    Cuidados:
        - Ação irreversível
        - Cliques e sessões associados podem ficar órfãos
        - Considerar soft delete (status=archived) em produção
    """
    if not await repo.exists(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    await repo.delete(post_id)
    return MessageResponse(message="Post removido com sucesso")
