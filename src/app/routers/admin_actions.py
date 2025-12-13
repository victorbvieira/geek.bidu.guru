"""
Rotas de acao (POST/DELETE) para painel administrativo.

Processa formularios de criacao, edicao e exclusao de:
- Posts, Produtos, Categorias e Usuarios
"""

import json
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from starlette import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CategoryRepo,
    DBSession,
    OccasionRepo,
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


def extract_product_slugs_from_content(content: str) -> list[str]:
    """
    Extrai slugs de produtos do conteudo do post.

    Busca por padroes [product:slug-do-produto] no conteudo.

    Args:
        content: Conteudo do post em markdown

    Returns:
        Lista de slugs unicos encontrados
    """
    import re

    if not content:
        return []

    # Pattern para [product:slug-do-produto]
    pattern = r'\[product:([a-zA-Z0-9_-]+)\]'
    matches = re.findall(pattern, content)

    # Remove duplicados mantendo ordem
    seen = set()
    unique_slugs = []
    for slug in matches:
        if slug not in seen:
            seen.add(slug)
            unique_slugs.append(slug)

    return unique_slugs


@router.post("/posts", response_class=RedirectResponse)
async def create_post(
    request: Request,
    current_user: AdminUser,
    repo: PostRepo,
    product_repo: ProductRepo,
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

    # Extrai e vincula produtos do conteudo automaticamente
    product_slugs = extract_product_slugs_from_content(content)
    if product_slugs:
        product_ids = await product_repo.get_ids_by_slugs(product_slugs)
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
    product_repo: ProductRepo,
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

    # Extrai e atualiza produtos vinculados do conteudo automaticamente
    product_slugs = extract_product_slugs_from_content(content)
    product_ids = []
    if product_slugs:
        product_ids = await product_repo.get_ids_by_slugs(product_slugs)
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
    images: str = Form("[]"),
    rating: str = Form(""),
    review_count: str = Form(""),
    tags: str = Form(""),
    categories_json: str = Form("[]"),
):
    """Cria novo produto."""
    platform_enum = ProductPlatform(platform)
    platform_id = platform_product_id.strip() or None

    # Valida duplicidade: mesmo produto na mesma plataforma
    if platform_id and await repo.platform_product_exists(platform_enum, platform_id):
        raise HTTPException(
            status_code=400,
            detail=f"Ja existe um produto com ID '{platform_id}' na plataforma {platform}",
        )

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

    # Processa lista de imagens
    images_list = json.loads(images) if images else []
    main_image = images_list[0] if images_list else None

    # Processa lista de categorias (slugs)
    categories_list = json.loads(categories_json) if categories_json else []

    # Monta dados do produto
    product_data = {
        "name": name.strip(),
        "slug": product_slug,
        "affiliate_url_raw": affiliate_url_raw.strip(),
        "affiliate_redirect_slug": redirect_slug,
        "platform": platform_enum,
        "short_description": short_description.strip() or None,
        "long_description": long_description.strip() or None,
        "platform_product_id": platform_id,
        "price": float(price) if price else None,
        "availability": ProductAvailability(availability),
        "main_image_url": main_image,
        "images": images_list,
        "categories": categories_list,
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
    images: str = Form("[]"),
    rating: str = Form(""),
    review_count: str = Form(""),
    tags: str = Form(""),
    categories_json: str = Form("[]"),
):
    """Atualiza produto existente."""
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    platform_enum = ProductPlatform(platform)
    platform_id = platform_product_id.strip() or None

    # Valida duplicidade: mesmo produto na mesma plataforma (excluindo o atual)
    if platform_id and await repo.platform_product_exists(platform_enum, platform_id, exclude_id=product_id):
        raise HTTPException(
            status_code=400,
            detail=f"Ja existe outro produto com ID '{platform_id}' na plataforma {platform}",
        )

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

    # Processa lista de imagens
    images_list = json.loads(images) if images else []
    main_image = images_list[0] if images_list else None

    # Processa lista de categorias (slugs)
    try:
        categories_list = json.loads(categories_json) if categories_json else []
    except json.JSONDecodeError:
        categories_list = []

    # Monta dados de atualizacao
    update_data = {
        "name": name.strip(),
        "slug": product_slug,
        "affiliate_url_raw": affiliate_url_raw.strip(),
        "affiliate_redirect_slug": redirect_slug,
        "platform": platform_enum,
        "short_description": short_description.strip() or None,
        "long_description": long_description.strip() or None,
        "platform_product_id": platform_id,
        "price": float(price) if price else None,
        "availability": ProductAvailability(availability),
        "main_image_url": main_image,
        "images": images_list,
        "categories": categories_list,
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
    slug: str = Form(""),
    description: str = Form(""),
    parent_id: str = Form(""),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    image_url: str = Form(""),
):
    """Cria nova categoria."""
    # Gera slug automaticamente se nao fornecido
    category_slug = slug.strip() if slug.strip() else generate_slug(name)

    # Verifica se slug ja existe
    if await repo.slug_exists(category_slug):
        base_slug = category_slug
        counter = 1
        while await repo.slug_exists(category_slug):
            category_slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados da categoria com todos os campos
    category_data = {
        "name": name.strip(),
        "slug": category_slug,
        "description": description.strip() or None,
        "parent_id": UUID(parent_id) if parent_id else None,
        "image_url": image_url.strip() or None,
        "seo_title": seo_title.strip() or None,
        "seo_description": seo_description.strip() or None,
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
    slug: str = Form(""),
    description: str = Form(""),
    parent_id: str = Form(""),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    image_url: str = Form(""),
):
    """Atualiza categoria existente."""
    category = await repo.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    # Gera slug automaticamente se nao fornecido
    category_slug = slug.strip() if slug.strip() else generate_slug(name)

    # Verifica se slug ja existe (excluindo a categoria atual)
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

    # Monta dados de atualizacao com todos os campos
    update_data = {
        "name": name.strip(),
        "slug": category_slug,
        "description": description.strip() or None,
        "parent_id": new_parent_id,
        "image_url": image_url.strip() or None,
        "seo_title": seo_title.strip() or None,
        "seo_description": seo_description.strip() or None,
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


# -----------------------------------------------------------------------------
# Upload de Imagens
# -----------------------------------------------------------------------------


@router.post("/upload/image")
async def upload_image(
    current_user: AdminUser,
    file: UploadFile = File(...),
):
    """
    Upload de imagem para produtos.

    A imagem e automaticamente redimensionada para 800x800 px (1:1).
    Aceita: JPEG, PNG, WebP, GIF
    Tamanho maximo: 5MB

    Returns:
        JSON com URL da imagem salva
    """
    from app.services.upload import save_product_image

    # Usa resize=True para padronizar em 800x800
    image_url = await save_product_image(file, resize=True)

    return JSONResponse(
        content={"url": image_url, "message": "Imagem enviada com sucesso"},
        status_code=http_status.HTTP_201_CREATED,
    )


@router.post("/upload/category-image")
async def upload_category_image(
    current_user: AdminUser,
    file: UploadFile = File(...),
):
    """
    Upload de imagem para categorias.

    A imagem e automaticamente redimensionada para 400x400 px.
    Aceita: JPEG, PNG, WebP, GIF
    Tamanho maximo: 5MB

    Returns:
        JSON com URL da imagem salva
    """
    from app.services.upload import save_category_image

    image_url = await save_category_image(file)

    return JSONResponse(
        content={"url": image_url, "message": "Imagem enviada com sucesso"},
        status_code=http_status.HTTP_201_CREATED,
    )


@router.post("/upload/post-image")
async def upload_post_image(
    current_user: AdminUser,
    file: UploadFile = File(...),
):
    """
    Upload de imagem de destaque para posts.

    A imagem e automaticamente redimensionada para 1200x630 px (Open Graph).
    Aceita: JPEG, PNG, WebP, GIF
    Tamanho maximo: 5MB

    Returns:
        JSON com URL da imagem salva
    """
    from app.services.upload import save_post_image

    image_url = await save_post_image(file)

    return JSONResponse(
        content={"url": image_url, "message": "Imagem enviada com sucesso"},
        status_code=http_status.HTTP_201_CREATED,
    )


# -----------------------------------------------------------------------------
# API Endpoints (JSON) - Para AJAX
# -----------------------------------------------------------------------------


@router.post("/api/categories")
async def api_create_category(
    request: Request,
    current_user: AdminUser,
    repo: CategoryRepo,
):
    """
    Cria nova categoria via AJAX.

    Aceita JSON com: name, slug (opcional), description (opcional), image_url (opcional)

    Returns:
        JSON com dados da categoria criada
    """
    data = await request.json()

    name = data.get("name", "").strip()
    if not name:
        return JSONResponse(
            content={"detail": "Nome da categoria e obrigatorio"},
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )

    # Gera slug se nao fornecido
    slug = data.get("slug")
    if slug:
        slug = slug.strip()
    else:
        slug = generate_slug(name)

    # Verifica se slug ja existe
    if await repo.slug_exists(slug):
        base_slug = slug
        counter = 1
        while await repo.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados da categoria
    category_data = {
        "name": name,
        "slug": slug,
        "description": data.get("description", "").strip() or None,
        "image_url": data.get("image_url", "").strip() or None,
        "parent_id": None,
    }

    category = await repo.create(category_data)

    return JSONResponse(
        content={
            "id": str(category.id),
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "image_url": category.image_url,
        },
        status_code=http_status.HTTP_201_CREATED,
    )


# -----------------------------------------------------------------------------
# Occasions - Create/Update/Delete
# -----------------------------------------------------------------------------


@router.post("/occasions", response_class=RedirectResponse)
async def create_occasion(
    request: Request,
    current_user: AdminUser,
    repo: OccasionRepo,
    name: str = Form(...),
    slug: str = Form(""),
    description: str = Form(""),
    icon: str = Form(""),
    image_url: str = Form(""),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    is_active: str = Form("on"),
    display_order: str = Form("0"),
):
    """Cria nova ocasiao."""
    # Gera slug se nao fornecido
    occasion_slug = slug.strip() if slug else generate_slug(name)

    # Verifica se slug ja existe
    if await repo.slug_exists(occasion_slug):
        base_slug = occasion_slug
        counter = 1
        while await repo.slug_exists(occasion_slug):
            occasion_slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados da ocasiao
    occasion_data = {
        "name": name.strip(),
        "slug": occasion_slug,
        "description": description.strip() or None,
        "icon": icon.strip() or None,
        "image_url": image_url.strip() or None,
        "seo_title": seo_title.strip() or None,
        "seo_description": seo_description.strip() or None,
        "is_active": is_active == "on",
        "display_order": int(display_order) if display_order else 0,
    }

    await repo.create(occasion_data)

    return RedirectResponse(
        url="/admin/occasions",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/occasions/{occasion_id}", response_class=RedirectResponse)
async def update_occasion(
    request: Request,
    occasion_id: UUID,
    current_user: AdminUser,
    repo: OccasionRepo,
    name: str = Form(...),
    slug: str = Form(""),
    description: str = Form(""),
    icon: str = Form(""),
    image_url: str = Form(""),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    is_active: str = Form(""),
    display_order: str = Form("0"),
):
    """Atualiza ocasiao existente."""
    occasion = await repo.get(occasion_id)
    if not occasion:
        raise HTTPException(status_code=404, detail="Ocasiao nao encontrada")

    # Gera slug se nao fornecido
    occasion_slug = slug.strip() if slug else generate_slug(name)

    # Verifica se slug ja existe (excluindo a ocasiao atual)
    if await repo.slug_exists(occasion_slug, exclude_id=occasion_id):
        base_slug = occasion_slug
        counter = 1
        while await repo.slug_exists(occasion_slug, exclude_id=occasion_id):
            occasion_slug = f"{base_slug}-{counter}"
            counter += 1

    # Monta dados de atualizacao
    update_data = {
        "name": name.strip(),
        "slug": occasion_slug,
        "description": description.strip() or None,
        "icon": icon.strip() or None,
        "image_url": image_url.strip() or None,
        "seo_title": seo_title.strip() or None,
        "seo_description": seo_description.strip() or None,
        "is_active": is_active == "on",
        "display_order": int(display_order) if display_order else 0,
    }

    await repo.update(occasion, update_data)

    return RedirectResponse(
        url="/admin/occasions",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


@router.post("/occasions/{occasion_id}/delete", response_class=RedirectResponse)
async def delete_occasion(
    request: Request,
    occasion_id: UUID,
    current_user: AdminUser,
    repo: OccasionRepo,
):
    """Exclui ocasiao."""
    deleted = await repo.delete(occasion_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ocasiao nao encontrada")

    return RedirectResponse(
        url="/admin/occasions",
        status_code=http_status.HTTP_303_SEE_OTHER,
    )


# -----------------------------------------------------------------------------
# Migracao de Uploads (TEMPORARIO)
# -----------------------------------------------------------------------------


@router.post("/migrate-uploads")
async def migrate_uploads(
    current_user: Annotated[User, Depends(require_admin_role)],
    db: DBSession,
):
    """
    Migra imagens do diretorio antigo para o novo.

    ROTA TEMPORARIA - Remover apos migracao completa.

    Esta rota:
    1. Copia arquivos de /app/src/app/static/uploads/* para /app/uploads/*
    2. Atualiza URLs no banco de dados (/static/uploads/ -> /uploads/)
    3. Retorna relatorio da migracao

    Requer: UPLOAD_DIR configurado e usuario admin.
    """
    import os
    import shutil
    from pathlib import Path
    from sqlalchemy import text

    from app.config import settings
    from app.core.logging import get_logger

    logger = get_logger(__name__)

    # Verifica se UPLOAD_DIR esta configurado (producao)
    if not settings.upload_dir:
        return JSONResponse(
            content={
                "success": False,
                "error": "UPLOAD_DIR nao configurado. Esta rota so funciona em producao.",
            },
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )

    # Diretorios
    old_base = Path("/app/src/app/static/uploads")
    new_base = Path(settings.upload_dir)

    # Relatorio
    report = {
        "files_copied": [],
        "files_skipped": [],
        "files_failed": [],
        "db_products_updated": 0,
        "db_categories_updated": 0,
        "db_posts_updated": 0,
    }

    # 1. Copiar arquivos fisicos
    if old_base.exists():
        for subdir in ["products", "categories", "posts"]:
            old_dir = old_base / subdir
            new_dir = new_base / subdir

            if not old_dir.exists():
                continue

            # Garante que diretorio destino existe
            new_dir.mkdir(parents=True, exist_ok=True)

            for file in old_dir.iterdir():
                if file.is_file():
                    dest_file = new_dir / file.name

                    # Se arquivo ja existe no destino, pula
                    if dest_file.exists():
                        report["files_skipped"].append(f"{subdir}/{file.name}")
                        continue

                    try:
                        shutil.copy2(file, dest_file)
                        report["files_copied"].append(f"{subdir}/{file.name}")
                        logger.info(f"Copiado: {file} -> {dest_file}")
                    except Exception as e:
                        report["files_failed"].append({
                            "file": f"{subdir}/{file.name}",
                            "error": str(e),
                        })
                        logger.error(f"Erro ao copiar {file}: {e}")
    else:
        logger.warning(f"Diretorio antigo nao existe: {old_base}")

    # 2. Atualizar URLs no banco de dados

    # Products - main_image_url e images (JSONB array)
    try:
        # Atualiza main_image_url
        result = await db.execute(
            text("""
                UPDATE products
                SET main_image_url = REPLACE(main_image_url, '/static/uploads/', '/uploads/')
                WHERE main_image_url LIKE '/static/uploads/%'
            """)
        )
        report["db_products_updated"] += result.rowcount

        # Atualiza array de images (JSONB)
        # Substitui /static/uploads/ por /uploads/ em cada elemento do array
        result = await db.execute(
            text("""
                UPDATE products
                SET images = (
                    SELECT jsonb_agg(
                        REPLACE(elem::text, '/static/uploads/', '/uploads/')::jsonb #>> '{}'
                    )
                    FROM jsonb_array_elements_text(images) AS elem
                )
                WHERE images IS NOT NULL
                AND images::text LIKE '%/static/uploads/%'
            """)
        )
        report["db_products_updated"] += result.rowcount

        logger.info(f"Products atualizados: {report['db_products_updated']}")
    except Exception as e:
        logger.error(f"Erro ao atualizar products: {e}")
        report["db_products_error"] = str(e)

    # Categories - image_url
    try:
        result = await db.execute(
            text("""
                UPDATE categories
                SET image_url = REPLACE(image_url, '/static/uploads/', '/uploads/')
                WHERE image_url LIKE '/static/uploads/%'
            """)
        )
        report["db_categories_updated"] = result.rowcount
        logger.info(f"Categories atualizadas: {report['db_categories_updated']}")
    except Exception as e:
        logger.error(f"Erro ao atualizar categories: {e}")
        report["db_categories_error"] = str(e)

    # Posts - featured_image_url
    try:
        result = await db.execute(
            text("""
                UPDATE posts
                SET featured_image_url = REPLACE(featured_image_url, '/static/uploads/', '/uploads/')
                WHERE featured_image_url LIKE '/static/uploads/%'
            """)
        )
        report["db_posts_updated"] = result.rowcount
        logger.info(f"Posts atualizados: {report['db_posts_updated']}")
    except Exception as e:
        logger.error(f"Erro ao atualizar posts: {e}")
        report["db_posts_error"] = str(e)

    # Commit das alteracoes
    await db.commit()

    logger.info(f"Migracao concluida: {report}")

    return JSONResponse(
        content={
            "success": True,
            "message": "Migracao concluida com sucesso",
            "report": report,
        },
        status_code=http_status.HTTP_200_OK,
    )


@router.get("/migrate-uploads")
async def migrate_uploads_page(
    request: Request,
    current_user: Annotated[User, Depends(require_admin_role)],
):
    """
    Pagina de migracao de uploads (TEMPORARIO).

    Exibe informacoes sobre a migracao e botao para executar.
    """
    from pathlib import Path
    from app.config import settings

    # Verifica estado atual
    upload_dir_configured = bool(settings.upload_dir)
    old_base = Path("/app/src/app/static/uploads")
    new_base = Path(settings.upload_dir) if settings.upload_dir else None

    # Conta arquivos em cada diretorio
    old_files = {"products": 0, "categories": 0, "posts": 0}
    new_files = {"products": 0, "categories": 0, "posts": 0}

    if old_base.exists():
        for subdir in old_files.keys():
            subdir_path = old_base / subdir
            if subdir_path.exists():
                old_files[subdir] = len(list(subdir_path.glob("*")))

    if new_base and new_base.exists():
        for subdir in new_files.keys():
            subdir_path = new_base / subdir
            if subdir_path.exists():
                new_files[subdir] = len(list(subdir_path.glob("*")))

    # HTML inline simples (rota temporaria, nao precisa de template separado)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Migracao de Uploads - Admin</title>
        <style>
            body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #1a1a2e; color: #eee; }}
            h1 {{ color: #00d4ff; }}
            .card {{ background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .success {{ color: #4ade80; }}
            .warning {{ color: #fbbf24; }}
            .error {{ color: #f87171; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ color: #00d4ff; }}
            button {{ background: #00d4ff; color: #1a1a2e; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }}
            button:hover {{ background: #00b8e6; }}
            button:disabled {{ background: #666; cursor: not-allowed; }}
            #result {{ margin-top: 20px; padding: 20px; background: #0f172a; border-radius: 8px; display: none; }}
            pre {{ background: #0a0a0a; padding: 15px; border-radius: 4px; overflow-x: auto; }}
            a {{ color: #00d4ff; }}
        </style>
    </head>
    <body>
        <h1>Migracao de Uploads</h1>
        <p><a href="/admin">&larr; Voltar ao Admin</a></p>

        <div class="card">
            <h2>Status Atual</h2>
            <table>
                <tr>
                    <th>Configuracao</th>
                    <th>Valor</th>
                </tr>
                <tr>
                    <td>UPLOAD_DIR configurado</td>
                    <td class="{'success' if upload_dir_configured else 'warning'}">
                        {'Sim: ' + str(settings.upload_dir) if upload_dir_configured else 'Nao (usando /static/uploads/)'}
                    </td>
                </tr>
                <tr>
                    <td>Diretorio antigo existe</td>
                    <td class="{'success' if old_base.exists() else 'warning'}">
                        {str(old_base)} - {'Sim' if old_base.exists() else 'Nao'}
                    </td>
                </tr>
                <tr>
                    <td>Diretorio novo existe</td>
                    <td class="{'success' if new_base and new_base.exists() else 'warning'}">
                        {str(new_base) if new_base else 'N/A'} - {'Sim' if new_base and new_base.exists() else 'Nao'}
                    </td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>Arquivos por Diretorio</h2>
            <table>
                <tr>
                    <th>Tipo</th>
                    <th>Antigo (/static/uploads/)</th>
                    <th>Novo (/uploads/)</th>
                </tr>
                <tr>
                    <td>Products</td>
                    <td>{old_files['products']}</td>
                    <td>{new_files['products']}</td>
                </tr>
                <tr>
                    <td>Categories</td>
                    <td>{old_files['categories']}</td>
                    <td>{new_files['categories']}</td>
                </tr>
                <tr>
                    <td>Posts</td>
                    <td>{old_files['posts']}</td>
                    <td>{new_files['posts']}</td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>Executar Migracao</h2>
            <p>A migracao ira:</p>
            <ol>
                <li>Copiar arquivos de <code>/app/src/app/static/uploads/*</code> para <code>/app/uploads/*</code></li>
                <li>Atualizar URLs no banco de dados (<code>/static/uploads/</code> &rarr; <code>/uploads/</code>)</li>
            </ol>
            <p class="warning">Arquivos ja existentes no destino serao ignorados (nao sobrescritos).</p>

            <button id="migrateBtn" onclick="runMigration()" {'disabled' if not upload_dir_configured else ''}>
                {'Executar Migracao' if upload_dir_configured else 'UPLOAD_DIR nao configurado'}
            </button>
        </div>

        <div id="result">
            <h2>Resultado</h2>
            <pre id="resultContent"></pre>
        </div>

        <script>
            async function runMigration() {{
                const btn = document.getElementById('migrateBtn');
                const result = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');

                btn.disabled = true;
                btn.textContent = 'Executando...';
                result.style.display = 'block';
                resultContent.textContent = 'Aguarde...';

                try {{
                    const response = await fetch('/admin/migrate-uploads', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    const data = await response.json();
                    resultContent.textContent = JSON.stringify(data, null, 2);

                    if (data.success) {{
                        btn.textContent = 'Migracao Concluida!';
                        btn.style.background = '#4ade80';
                    }} else {{
                        btn.textContent = 'Erro na Migracao';
                        btn.style.background = '#f87171';
                        btn.disabled = false;
                    }}
                }} catch (error) {{
                    resultContent.textContent = 'Erro: ' + error.message;
                    btn.textContent = 'Erro - Tentar Novamente';
                    btn.style.background = '#f87171';
                    btn.disabled = false;
                }}
            }}
        </script>
    </body>
    </html>
    """

    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)
