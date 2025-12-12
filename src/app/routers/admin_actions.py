"""
Rotas de acao (POST/DELETE) para painel administrativo.

Processa formularios de criacao, edicao e exclusao de:
- Posts, Produtos, Categorias e Usuarios
"""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CategoryRepo,
    DBSession,
    PostRepo,
    ProductRepo,
    UserRepo,
)
from app.core.security import get_password_hash
from app.models import User
from app.models.post import PostStatus, PostType
from app.models.product import ProductAvailability, ProductPlatform
from app.models.user import UserRole
from app.routers.admin import require_admin_user, require_admin_role

# Router para acoes do admin
router = APIRouter(prefix="/admin", tags=["admin-actions"])

# Type alias para usuario admin
AdminUser = Annotated[User, Depends(require_admin_user)]


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def generate_slug(text: str) -> str:
    """Gera slug a partir de texto."""
    import re
    import unicodedata

    # Normaliza unicode e remove acentos
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("ASCII")

    # Converte para lowercase e substitui espacos por hifens
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)

    return text


def parse_tags(tags_str: str) -> list[str]:
    """Converte string de tags separadas por virgula em lista."""
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]


def parse_datetime(dt_str: str) -> datetime | None:
    """Converte string datetime-local para datetime."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


# -----------------------------------------------------------------------------
# Posts - Create/Update/Delete
# -----------------------------------------------------------------------------


def parse_product_ids(products_str: str) -> list[UUID]:
    """Converte string de IDs de produtos separados por virgula em lista de UUIDs."""
    if not products_str:
        return []
    ids = []
    for id_str in products_str.split(","):
        id_str = id_str.strip()
        if id_str:
            try:
                ids.append(UUID(id_str))
            except ValueError:
                pass
    return ids


@router.post("/posts", response_class=RedirectResponse)
async def create_post(
    request: Request,
    current_user: AdminUser,
    repo: PostRepo,
    title: str = Form(...),
    content: str = Form(...),
    type: str = Form("listicle"),
    slug: str = Form(""),
    subtitle: str = Form(""),
    featured_image_url: str = Form(""),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    seo_focus_keyword: str = Form(""),
    category_id: str = Form(""),
    tags: str = Form(""),
    status: str = Form("draft"),
    publish_at: str = Form(""),
    products: str = Form(""),
):
    """Cria novo post."""
    # Gera slug se nao fornecido
    post_slug = slug.strip() if slug else generate_slug(title)

    # Verifica se slug ja existe
    if await repo.slug_exists(post_slug):
        # Adiciona sufixo numerico
        base_slug = post_slug
        counter = 1
        while await repo.slug_exists(post_slug):
            post_slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados do post
    post_data = {
        "title": title.strip(),
        "slug": post_slug,
        "content": content,
        "type": PostType(type),
        "subtitle": subtitle.strip() or None,
        "featured_image_url": featured_image_url.strip() or None,
        "seo_title": seo_title.strip() or None,
        "seo_description": seo_description.strip() or None,
        "seo_focus_keyword": seo_focus_keyword.strip() or None,
        "category_id": UUID(category_id) if category_id else None,
        "author_id": current_user.id,
        "tags": parse_tags(tags),
        "status": PostStatus(status),
        "publish_at": parse_datetime(publish_at),
    }

    post = await repo.create(post_data)

    # Vincula produtos ao post
    product_ids = parse_product_ids(products)
    if product_ids:
        await repo.set_post_products(post.id, product_ids)

    return RedirectResponse(
        url="/admin/posts",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/posts/{post_id}", response_class=RedirectResponse)
async def update_post(
    request: Request,
    post_id: UUID,
    current_user: AdminUser,
    repo: PostRepo,
    title: str = Form(...),
    content: str = Form(...),
    type: str = Form("listicle"),
    slug: str = Form(""),
    subtitle: str = Form(""),
    featured_image_url: str = Form(""),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    seo_focus_keyword: str = Form(""),
    category_id: str = Form(""),
    tags: str = Form(""),
    post_status: str = Form("draft", alias="status"),
    publish_at: str = Form(""),
    products: str = Form(""),
):
    """Atualiza post existente."""
    post = await repo.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post nao encontrado")

    # Gera slug se nao fornecido
    post_slug = slug.strip() if slug else generate_slug(title)

    # Verifica se slug ja existe (excluindo o post atual)
    if await repo.slug_exists(post_slug, exclude_id=post_id):
        base_slug = post_slug
        counter = 1
        while await repo.slug_exists(post_slug, exclude_id=post_id):
            post_slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados de atualizacao
    update_data = {
        "title": title.strip(),
        "slug": post_slug,
        "content": content,
        "type": PostType(type),
        "subtitle": subtitle.strip() or None,
        "featured_image_url": featured_image_url.strip() or None,
        "seo_title": seo_title.strip() or None,
        "seo_description": seo_description.strip() or None,
        "seo_focus_keyword": seo_focus_keyword.strip() or None,
        "category_id": UUID(category_id) if category_id else None,
        "tags": parse_tags(tags),
        "status": PostStatus(post_status),
        "publish_at": parse_datetime(publish_at),
    }

    await repo.update(post, update_data)

    # Atualiza produtos vinculados
    product_ids = parse_product_ids(products)
    await repo.set_post_products(post_id, product_ids)

    return RedirectResponse(
        url="/admin/posts",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/posts/{post_id}/delete", response_class=RedirectResponse)
async def delete_post(
    request: Request,
    post_id: UUID,
    current_user: AdminUser,
    repo: PostRepo,
):
    """Exclui post."""
    deleted = await repo.delete(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post nao encontrado")

    return RedirectResponse(
        url="/admin/posts",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


# -----------------------------------------------------------------------------
# Products - Create/Update/Delete
# -----------------------------------------------------------------------------


@router.post("/products", response_class=RedirectResponse)
async def create_product(
    request: Request,
    current_user: AdminUser,
    repo: ProductRepo,
    name: str = Form(...),
    affiliate_url_raw: str = Form(...),
    affiliate_redirect_slug: str = Form(...),
    platform: str = Form("amazon"),
    slug: str = Form(""),
    short_description: str = Form(""),
    long_description: str = Form(""),
    platform_product_id: str = Form(""),
    price: str = Form(""),
    availability: str = Form("available"),
    main_image_url: str = Form(""),
    rating: str = Form(""),
    review_count: str = Form(""),
    tags: str = Form(""),
):
    """Cria novo produto."""
    # Gera slug se nao fornecido
    product_slug = slug.strip() if slug else generate_slug(name)

    # Verifica se slug ja existe
    if await repo.slug_exists(product_slug):
        base_slug = product_slug
        counter = 1
        while await repo.slug_exists(product_slug):
            product_slug = f"{base_slug}-{counter}"
            counter += 1

    # Verifica se redirect_slug ja existe
    redirect_slug = affiliate_redirect_slug.strip()
    if await repo.redirect_slug_exists(redirect_slug):
        base_slug = redirect_slug
        counter = 1
        while await repo.redirect_slug_exists(redirect_slug):
            redirect_slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados do produto
    product_data = {
        "name": name.strip(),
        "slug": product_slug,
        "affiliate_url_raw": affiliate_url_raw.strip(),
        "affiliate_redirect_slug": redirect_slug,
        "platform": ProductPlatform(platform),
        "short_description": short_description.strip() or None,
        "long_description": long_description.strip() or None,
        "platform_product_id": platform_product_id.strip() or None,
        "price": float(price) if price else None,
        "availability": ProductAvailability(availability),
        "main_image_url": main_image_url.strip() or None,
        "rating": float(rating) if rating else None,
        "review_count": int(review_count) if review_count else 0,
        "tags": parse_tags(tags),
    }

    # Atualiza price_range baseado no preco
    product = await repo.create(product_data)
    if product.price:
        product.update_price_range()
        await repo.db.commit()

    return RedirectResponse(
        url="/admin/products",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/products/{product_id}", response_class=RedirectResponse)
async def update_product(
    request: Request,
    product_id: UUID,
    current_user: AdminUser,
    repo: ProductRepo,
    name: str = Form(...),
    affiliate_url_raw: str = Form(...),
    affiliate_redirect_slug: str = Form(...),
    platform: str = Form("amazon"),
    slug: str = Form(""),
    short_description: str = Form(""),
    long_description: str = Form(""),
    platform_product_id: str = Form(""),
    price: str = Form(""),
    availability: str = Form("available"),
    main_image_url: str = Form(""),
    rating: str = Form(""),
    review_count: str = Form(""),
    tags: str = Form(""),
):
    """Atualiza produto existente."""
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    # Gera slug se nao fornecido
    product_slug = slug.strip() if slug else generate_slug(name)

    # Verifica se slug ja existe (excluindo o produto atual)
    if await repo.slug_exists(product_slug, exclude_id=product_id):
        base_slug = product_slug
        counter = 1
        while await repo.slug_exists(product_slug, exclude_id=product_id):
            product_slug = f"{base_slug}-{counter}"
            counter += 1

    # Verifica redirect_slug
    redirect_slug = affiliate_redirect_slug.strip()
    if await repo.redirect_slug_exists(redirect_slug, exclude_id=product_id):
        base_slug = redirect_slug
        counter = 1
        while await repo.redirect_slug_exists(redirect_slug, exclude_id=product_id):
            redirect_slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados de atualizacao
    update_data = {
        "name": name.strip(),
        "slug": product_slug,
        "affiliate_url_raw": affiliate_url_raw.strip(),
        "affiliate_redirect_slug": redirect_slug,
        "platform": ProductPlatform(platform),
        "short_description": short_description.strip() or None,
        "long_description": long_description.strip() or None,
        "platform_product_id": platform_product_id.strip() or None,
        "price": float(price) if price else None,
        "availability": ProductAvailability(availability),
        "main_image_url": main_image_url.strip() or None,
        "rating": float(rating) if rating else None,
        "review_count": int(review_count) if review_count else 0,
        "tags": parse_tags(tags),
    }

    await repo.update(product, update_data)

    # Atualiza price_range
    if product.price:
        product.update_price_range()
        await repo.db.commit()

    return RedirectResponse(
        url="/admin/products",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/products/{product_id}/delete", response_class=RedirectResponse)
async def delete_product(
    request: Request,
    product_id: UUID,
    current_user: AdminUser,
    repo: ProductRepo,
):
    """Exclui produto."""
    deleted = await repo.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    return RedirectResponse(
        url="/admin/products",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


# -----------------------------------------------------------------------------
# Categories - Create/Update/Delete
# -----------------------------------------------------------------------------


@router.post("/categories", response_class=RedirectResponse)
async def create_category(
    request: Request,
    current_user: AdminUser,
    repo: CategoryRepo,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    parent_id: str = Form(""),
    # Campos SEO e image_url podem ser enviados mas serao ignorados
    # ate que o modelo Category seja atualizado com esses campos
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    image_url: str = Form(""),
):
    """Cria nova categoria."""
    # Verifica se slug ja existe
    category_slug = slug.strip()
    if await repo.slug_exists(category_slug):
        base_slug = category_slug
        counter = 1
        while await repo.slug_exists(category_slug):
            category_slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados da categoria (apenas campos que existem no modelo)
    category_data = {
        "name": name.strip(),
        "slug": category_slug,
        "description": description.strip() or None,
        "parent_id": UUID(parent_id) if parent_id else None,
    }

    await repo.create(category_data)

    return RedirectResponse(
        url="/admin/categories",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/categories/{category_id}", response_class=RedirectResponse)
async def update_category(
    request: Request,
    category_id: UUID,
    current_user: AdminUser,
    repo: CategoryRepo,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    parent_id: str = Form(""),
    # Campos SEO e image_url podem ser enviados mas serao ignorados
    # ate que o modelo Category seja atualizado com esses campos
    seo_title: str = Form(""),  # noqa: ARG001
    seo_description: str = Form(""),  # noqa: ARG001
    image_url: str = Form(""),  # noqa: ARG001
):
    """Atualiza categoria existente."""
    category = await repo.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    # Verifica se slug ja existe (excluindo a categoria atual)
    category_slug = slug.strip()
    if await repo.slug_exists(category_slug, exclude_id=category_id):
        base_slug = category_slug
        counter = 1
        while await repo.slug_exists(category_slug, exclude_id=category_id):
            category_slug = f"{base_slug}-{counter}"
            counter += 1

    # Evita categoria ser pai de si mesma
    new_parent_id = UUID(parent_id) if parent_id else None
    if new_parent_id == category_id:
        new_parent_id = None

    # Monta dados de atualizacao (apenas campos que existem no modelo)
    update_data = {
        "name": name.strip(),
        "slug": category_slug,
        "description": description.strip() or None,
        "parent_id": new_parent_id,
    }

    await repo.update(category, update_data)

    return RedirectResponse(
        url="/admin/categories",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/categories/{category_id}/delete", response_class=RedirectResponse)
async def delete_category(
    request: Request,
    category_id: UUID,
    current_user: AdminUser,
    repo: CategoryRepo,
):
    """Exclui categoria."""
    deleted = await repo.delete(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    return RedirectResponse(
        url="/admin/categories",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


# -----------------------------------------------------------------------------
# Users - Create/Update/Delete (Admin only)
# -----------------------------------------------------------------------------


@router.post("/users", response_class=RedirectResponse)
async def create_user(
    request: Request,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: UserRepo,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    role: str = Form("author"),
    is_active: str = Form(""),
):
    """Cria novo usuario (apenas admin)."""
    # Valida senhas
    if password != password_confirm:
        raise HTTPException(status_code=400, detail="Senhas nao conferem")

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Senha deve ter no minimo 8 caracteres")

    # Verifica se email ja existe
    existing = await repo.get_by_email(email.strip())
    if existing:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")

    # Monta dados do usuario
    user_data = {
        "name": name.strip(),
        "email": email.strip().lower(),
        "password_hash": get_password_hash(password),
        "role": UserRole(role),
        "is_active": is_active == "1",
    }

    await repo.create(user_data)

    return RedirectResponse(
        url="/admin/users",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/users/{user_id}", response_class=RedirectResponse)
async def update_user(
    request: Request,
    user_id: UUID,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: UserRepo,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(""),
    role: str = Form("author"),
    is_active: str = Form(""),
):
    """Atualiza usuario existente (apenas admin)."""
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    # Verifica se email ja existe (excluindo o usuario atual)
    existing = await repo.get_by_email(email.strip())
    if existing and existing.id != user_id:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")

    # Monta dados de atualizacao
    update_data = {
        "name": name.strip(),
        "email": email.strip().lower(),
        "role": UserRole(role),
        "is_active": is_active == "1",
    }

    # Atualiza senha se fornecida
    if password:
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Senha deve ter no minimo 8 caracteres")
        update_data["password_hash"] = get_password_hash(password)

    await repo.update(user, update_data)

    return RedirectResponse(
        url="/admin/users",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/users/{user_id}/delete", response_class=RedirectResponse)
async def delete_user(
    request: Request,
    user_id: UUID,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: UserRepo,
):
    """Exclui usuario (apenas admin)."""
    # Nao permite excluir a si mesmo
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Nao e possivel excluir a si mesmo")

    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    return RedirectResponse(
        url="/admin/users",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )
