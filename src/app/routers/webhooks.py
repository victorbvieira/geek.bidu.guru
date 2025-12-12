"""
Router de Webhooks para integracao com n8n.

Este modulo fornece endpoints seguros para o n8n (ou outras ferramentas de automacao)
interagir com o sistema. Todos os endpoints requerem autenticacao via API Key ou JWT.

Endpoints disponiveis:
    POST /webhooks/n8n/posts         - Criar post via automacao
    POST /webhooks/n8n/products      - Criar/atualizar produto
    POST /webhooks/n8n/price-update  - Atualizar preco de produto
    GET  /webhooks/n8n/health        - Health check para n8n

Autenticacao:
    - Header: X-N8N-API-Key (configurado em N8N_API_KEY no .env)
    - Ou: Bearer token JWT de usuario com role AUTOMATION

Configuracao no n8n:
    1. No n8n, use o node "HTTP Request"
    2. Configure o header X-N8N-API-Key com o valor da variavel N8N_API_KEY
    3. Ou use autenticacao Bearer com token JWT do usuario automation
"""

import hmac
import logging
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.post import Post, PostStatus, PostType
from app.models.product import Product, ProductAvailability, ProductPlatform
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/n8n", tags=["webhooks"])


# -----------------------------------------------------------------------------
# Schemas para Webhooks
# -----------------------------------------------------------------------------


class WebhookPostCreate(BaseModel):
    """Schema para criacao de post via webhook n8n."""

    title: str = Field(..., min_length=5, max_length=200)
    slug: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=100)
    subtitle: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    post_type: PostType = PostType.PRODUCT_SINGLE
    status: PostStatus = PostStatus.DRAFT
    featured_image_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    product_ids: list[str] = Field(default_factory=list)  # UUIDs como string


class WebhookProductCreate(BaseModel):
    """Schema para criacao/atualizacao de produto via webhook n8n."""

    name: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=200)
    short_description: str | None = None
    long_description: str | None = None
    current_price: float | None = None
    original_price: float | None = None
    affiliate_url: str
    image_url: str | None = None
    platform: ProductPlatform = ProductPlatform.AMAZON
    availability: ProductAvailability = ProductAvailability.AVAILABLE
    tags: list[str] = Field(default_factory=list)


class WebhookPriceUpdate(BaseModel):
    """Schema para atualizacao de preco via webhook n8n."""

    product_id: str | None = None  # UUID como string
    slug: str | None = None  # Alternativa ao ID
    current_price: float
    original_price: float | None = None
    availability: ProductAvailability | None = None


class WebhookResponse(BaseModel):
    """Resposta padrao dos webhooks."""

    success: bool
    message: str
    data: dict | None = None


# -----------------------------------------------------------------------------
# Dependencias de Autenticacao
# -----------------------------------------------------------------------------


async def verify_n8n_api_key(
    x_n8n_api_key: Annotated[str | None, Header()] = None,
) -> bool:
    """
    Verifica a API Key do n8n.

    A API Key deve ser configurada em N8N_API_KEY no .env.
    O n8n deve enviar o header X-N8N-API-Key com este valor.
    """
    # Se nao tiver API Key configurada, desabilita autenticacao por API Key
    n8n_api_key = getattr(settings, "n8n_api_key", None)

    if not n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="N8N_API_KEY nao configurada no servidor",
        )

    if not x_n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header X-N8N-API-Key obrigatorio",
        )

    # Comparacao segura contra timing attacks
    if not hmac.compare_digest(x_n8n_api_key, n8n_api_key):
        logger.warning("Tentativa de acesso com API Key invalida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key invalida",
        )

    return True


async def get_automation_user(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Retorna o usuario de automacao do sistema.

    Este usuario e usado para registrar acoes feitas via n8n.
    """
    result = await session.execute(
        select(User).where(
            User.role == UserRole.AUTOMATION, User.is_active == True  # noqa: E712
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Usuario de automacao nao encontrado. Execute o seed primeiro.",
        )

    return user


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------


@router.get("/health", response_model=WebhookResponse)
async def webhook_health_check(
    _: Annotated[bool, Depends(verify_n8n_api_key)],
) -> WebhookResponse:
    """
    Health check para o n8n verificar se o webhook esta disponivel.

    Retorna informacoes basicas sobre o status do sistema.
    """
    return WebhookResponse(
        success=True,
        message="Webhook n8n operacional",
        data={
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0.0",
        },
    )


@router.post("/posts", response_model=WebhookResponse)
async def webhook_create_post(
    payload: WebhookPostCreate,
    _: Annotated[bool, Depends(verify_n8n_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
    automation_user: Annotated[User, Depends(get_automation_user)],
) -> WebhookResponse:
    """
    Cria um novo post via webhook do n8n.

    O post sera criado com o usuario de automacao como autor.
    Ideal para workflows de geracao automatica de conteudo.
    """
    # Verificar se slug ja existe
    existing = await session.execute(select(Post).where(Post.slug == payload.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Post com slug '{payload.slug}' ja existe",
        )

    # Criar post
    post = Post(
        title=payload.title,
        slug=payload.slug,
        content=payload.content,
        subtitle=payload.subtitle,
        seo_title=payload.seo_title or payload.title[:60] if payload.seo_title else payload.title[:60],
        seo_description=payload.seo_description,
        type=payload.post_type,  # O modelo usa 'type', nao 'post_type'
        status=payload.status,
        featured_image_url=payload.featured_image_url,
        tags=payload.tags,
        author_id=automation_user.id,
    )

    # Se publicado, definir data de publicacao
    if payload.status == PostStatus.PUBLISHED:
        post.publish_at = datetime.now(UTC)  # O modelo usa 'publish_at'

    session.add(post)
    await session.commit()
    await session.refresh(post)

    logger.info(f"Post criado via n8n: {post.slug} (ID: {post.id})")

    return WebhookResponse(
        success=True,
        message="Post criado com sucesso",
        data={
            "id": str(post.id),
            "slug": post.slug,
            "status": post.status.value,
        },
    )


@router.post("/products", response_model=WebhookResponse)
async def webhook_create_or_update_product(
    payload: WebhookProductCreate,
    _: Annotated[bool, Depends(verify_n8n_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WebhookResponse:
    """
    Cria ou atualiza um produto via webhook do n8n.

    Se o slug ja existir, atualiza o produto existente.
    Ideal para sincronizacao de produtos com APIs de afiliados.
    """
    # Verificar se produto ja existe pelo slug
    result = await session.execute(select(Product).where(Product.slug == payload.slug))
    product = result.scalar_one_or_none()

    if product:
        # Atualizar produto existente
        product.name = payload.name
        product.short_description = payload.short_description
        product.long_description = payload.long_description
        product.price = payload.current_price  # O modelo usa 'price'
        product.affiliate_url_raw = payload.affiliate_url  # O modelo usa 'affiliate_url_raw'
        product.main_image_url = payload.image_url  # O modelo usa 'main_image_url'
        product.platform = payload.platform
        product.availability = payload.availability
        product.tags = payload.tags
        product.last_price_update = datetime.now(UTC)  # O modelo usa 'last_price_update'

        await session.commit()
        await session.refresh(product)

        logger.info(f"Produto atualizado via n8n: {product.slug} (ID: {product.id})")

        return WebhookResponse(
            success=True,
            message="Produto atualizado com sucesso",
            data={
                "id": str(product.id),
                "slug": product.slug,
                "action": "updated",
            },
        )
    else:
        # Criar novo produto - gera redirect slug automaticamente
        import secrets
        redirect_slug = f"{payload.slug}-{secrets.token_hex(4)}"

        product = Product(
            name=payload.name,
            slug=payload.slug,
            short_description=payload.short_description,
            long_description=payload.long_description,
            price=payload.current_price,  # O modelo usa 'price'
            affiliate_url_raw=payload.affiliate_url,  # O modelo usa 'affiliate_url_raw'
            affiliate_redirect_slug=redirect_slug,  # Campo obrigatorio
            main_image_url=payload.image_url,  # O modelo usa 'main_image_url'
            platform=payload.platform,
            availability=payload.availability,
            tags=payload.tags,
        )

        session.add(product)
        await session.commit()
        await session.refresh(product)

        logger.info(f"Produto criado via n8n: {product.slug} (ID: {product.id})")

        return WebhookResponse(
            success=True,
            message="Produto criado com sucesso",
            data={
                "id": str(product.id),
                "slug": product.slug,
                "action": "created",
            },
        )


@router.post("/price-update", response_model=WebhookResponse)
async def webhook_update_price(
    payload: WebhookPriceUpdate,
    _: Annotated[bool, Depends(verify_n8n_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WebhookResponse:
    """
    Atualiza preco de um produto via webhook do n8n.

    Pode identificar o produto por ID ou slug.
    Ideal para workflows de atualizacao periodica de precos.
    """
    # Buscar produto por ID ou slug
    if payload.product_id:
        try:
            product_uuid = UUID(payload.product_id)
            result = await session.execute(
                select(Product).where(Product.id == product_uuid)
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_id invalido (deve ser UUID)",
            )
    elif payload.slug:
        result = await session.execute(
            select(Product).where(Product.slug == payload.slug)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe product_id ou slug",
        )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Registrar preco anterior para log
    old_price = product.price  # O modelo usa 'price'

    # Atualizar preco
    product.price = payload.current_price  # O modelo usa 'price'
    if payload.availability is not None:
        product.availability = payload.availability
    product.last_price_update = datetime.now(UTC)  # O modelo usa 'last_price_update'

    await session.commit()

    logger.info(
        f"Preco atualizado via n8n: {product.slug} "
        f"({old_price} -> {payload.current_price})"
    )

    return WebhookResponse(
        success=True,
        message="Preco atualizado com sucesso",
        data={
            "id": str(product.id),
            "slug": product.slug,
            "old_price": old_price,
            "new_price": payload.current_price,
        },
    )
