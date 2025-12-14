"""
Rotas SSR para painel administrativo.

Renderiza templates HTML para:
- Dashboard com metricas
- CRUD de posts, produtos, categorias e usuarios
- Login/logout do admin
"""

from pathlib import Path
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    AIConfigRepo,
    CategoryRepo,
    DBSession,
    OccasionRepo,
    Pagination,
    PostRepo,
    ProductRepo,
    UserRepo,
    pagination_params,
)
from app.core.deps import get_current_active_user, get_current_user, require_role
from app.core.security import (
    create_access_token,
    create_refresh_token,
    should_renew_token,
    verify_password,
)
from app.models import User
from app.models.post import PostStatus
from app.models.user import UserRole

# Router para rotas do admin
router = APIRouter(prefix="/admin", tags=["admin"])

# Templates (caminho absoluto)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# -----------------------------------------------------------------------------
# Dependencias de autenticacao para Admin (via cookies)
# -----------------------------------------------------------------------------


async def get_admin_user_from_cookie(
    request: Request,
    db: DBSession,
) -> tuple[Optional[User], Optional[dict]]:
    """
    Extrai usuario do cookie de sessao do admin.

    Retorna tupla (user, payload) onde:
    - user: Usuario autenticado ou None
    - payload: Payload do token JWT (para verificar renovacao) ou None
    """
    from app.core.security import verify_token
    from app.repositories.user import UserRepository

    token = request.cookies.get("admin_token")
    if not token:
        return None, None

    payload = verify_token(token, token_type="access")
    if payload is None:
        return None, None

    user_id = payload.get("sub")
    if not user_id:
        return None, None

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return None, None

    repo = UserRepository(db)
    user = await repo.get(user_uuid)

    if not user or not user.is_active:
        return None, None

    # Verificar se tem permissao de admin (admin ou editor)
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return None, None

    return user, payload


class AdminRedirectException(Exception):
    """Exception para redirecionar ao login."""

    pass


async def require_admin_user(
    request: Request,
    db: DBSession,
) -> User:
    """
    Requer usuario autenticado no admin.

    Levanta AdminRedirectException para redirect ao login.
    """
    user, _payload = await get_admin_user_from_cookie(request, db)
    if not user:
        raise AdminRedirectException()
    return user


AdminUser = Annotated[User, Depends(require_admin_user)]


# -----------------------------------------------------------------------------
# Login / Logout
# -----------------------------------------------------------------------------


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    db: DBSession,
    error: Optional[str] = None,
):
    """Pagina de login do admin."""
    # Se ja esta autenticado, redireciona pro dashboard
    user, _payload = await get_admin_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "title": "Login - Admin",
            "error": error,
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    db: DBSession,
    email: str = Form(...),
    password: str = Form(...),
):
    """Processa login do admin."""
    from app.repositories.user import UserRepository

    repo = UserRepository(db)
    user = await repo.get_by_email(email)

    # Validar credenciais
    error_msg = None
    if not user:
        error_msg = "Email ou senha incorretos"
    elif not verify_password(password, user.password_hash):
        error_msg = "Email ou senha incorretos"
    elif not user.is_active:
        error_msg = "Usuario inativo"
    elif user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        error_msg = "Acesso restrito a administradores"

    if error_msg:
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={
                "title": "Login - Admin",
                "error": error_msg,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Criar token
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value},
    )

    # Configuracao do cookie baseada no ambiente
    # Em producao: secure=True (apenas HTTPS)
    # Em desenvolvimento: secure=False (permite HTTP)
    from app.config import settings

    is_production = settings.environment == "production"
    # Tempo de expiracao do cookie igual ao JWT (em segundos)
    cookie_max_age = settings.jwt_access_token_expire_minutes * 60

    # Redirect com cookie
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="admin_token",
        value=access_token,
        httponly=True,
        secure=is_production,  # True apenas em producao (HTTPS)
        samesite="lax",
        max_age=cookie_max_age,
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    """Logout do admin."""
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="admin_token")
    return response


# -----------------------------------------------------------------------------
# Dashboard
# -----------------------------------------------------------------------------


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: AdminUser,
    post_repo: PostRepo,
    product_repo: ProductRepo,
):
    """Dashboard do admin com metricas."""
    # Buscar metricas
    total_posts = await post_repo.count()
    published_posts = await post_repo.count_published()
    total_products = await product_repo.count()
    total_clicks = await product_repo.sum_clicks()

    # Posts recentes
    recent_posts = await post_repo.get_multi(skip=0, limit=5)

    # Produtos mais clicados (top 5)
    top_products = await product_repo.get_top_clicked(limit=5)

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "title": "Dashboard - Admin",
            "current_user": current_user,
            "stats": {
                "total_posts": total_posts,
                "published_posts": published_posts,
                "total_products": total_products,
                "total_clicks": total_clicks,
            },
            "recent_posts": recent_posts,
            "top_products": top_products,
        },
    )


# -----------------------------------------------------------------------------
# Posts
# -----------------------------------------------------------------------------


@router.get("/posts", response_class=HTMLResponse)
async def list_posts(
    request: Request,
    current_user: AdminUser,
    repo: PostRepo,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    type_filter: Optional[str] = Query(None, alias="type"),
):
    """Listagem de posts com filtros por status e tipo."""
    from app.models.post import PostType

    skip = (page - 1) * per_page

    # Filtros
    filters = {}
    if status_filter:
        try:
            filters["status"] = PostStatus(status_filter)
        except ValueError:
            pass
    if type_filter:
        try:
            filters["type"] = PostType(type_filter)
        except ValueError:
            pass

    # Buscar posts
    if q:
        posts = await repo.search(q, skip=skip, limit=per_page)
        total = await repo.count_search(q)
    else:
        posts = await repo.get_multi(skip=skip, limit=per_page, **filters)
        total = await repo.count(**filters)

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="admin/posts/list.html",
        context={
            "title": "Posts - Admin",
            "current_user": current_user,
            "posts": posts,
            "q": q,
            "status": status_filter,
            "post_type": type_filter,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        },
    )


@router.get("/posts/new", response_class=HTMLResponse)
async def new_post(
    request: Request,
    current_user: AdminUser,
    category_repo: CategoryRepo,
    product_repo: ProductRepo,
):
    """Formulario de novo post."""
    categories = await category_repo.get_all()
    products = await product_repo.get_multi(limit=100)

    return templates.TemplateResponse(
        request=request,
        name="admin/posts/form.html",
        context={
            "title": "Novo Post - Admin",
            "current_user": current_user,
            "post": None,
            "categories": categories,
            "products": products,
            "selected_product_ids": [],
        },
    )


@router.get("/posts/{post_id}", response_class=HTMLResponse)
async def edit_post(
    request: Request,
    post_id: UUID,
    current_user: AdminUser,
    post_repo: PostRepo,
    category_repo: CategoryRepo,
    product_repo: ProductRepo,
):
    """Formulario de edicao de post."""
    post = await post_repo.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post nao encontrado")

    categories = await category_repo.get_all()
    products = await product_repo.get_multi(limit=100)
    selected_product_ids = await post_repo.get_post_product_ids(post_id)

    return templates.TemplateResponse(
        request=request,
        name="admin/posts/form.html",
        context={
            "title": f"Editar: {post.title} - Admin",
            "current_user": current_user,
            "post": post,
            "categories": categories,
            "products": products,
            "selected_product_ids": selected_product_ids,
        },
    )


# -----------------------------------------------------------------------------
# Produtos
# -----------------------------------------------------------------------------


@router.get("/products", response_class=HTMLResponse)
async def list_products(
    request: Request,
    current_user: AdminUser,
    repo: ProductRepo,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
    platform: Optional[str] = None,
    availability: Optional[str] = None,
):
    """Listagem de produtos."""
    skip = (page - 1) * per_page

    # Filtros
    filters = {}
    if platform:
        filters["platform"] = platform
    if availability:
        filters["availability"] = availability

    # Buscar produtos
    if q:
        products = await repo.search(q, skip=skip, limit=per_page)
        total = await repo.count_search(q)
    else:
        products = await repo.get_multi(skip=skip, limit=per_page, **filters)
        total = await repo.count(**filters)

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="admin/products/list.html",
        context={
            "title": "Produtos - Admin",
            "current_user": current_user,
            "products": products,
            "q": q,
            "platform": platform,
            "availability": availability,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        },
    )


@router.get("/products/new", response_class=HTMLResponse)
async def new_product(
    request: Request,
    current_user: AdminUser,
    category_repo: CategoryRepo,
):
    """Formulario de novo produto."""
    categories = await category_repo.get_all()

    return templates.TemplateResponse(
        request=request,
        name="admin/products/form.html",
        context={
            "title": "Novo Produto - Admin",
            "current_user": current_user,
            "product": None,
            "categories": categories,
        },
    )


@router.get("/products/{product_id}", response_class=HTMLResponse)
async def edit_product(
    request: Request,
    product_id: UUID,
    current_user: AdminUser,
    repo: ProductRepo,
    category_repo: CategoryRepo,
):
    """Formulario de edicao de produto."""
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    categories = await category_repo.get_all()

    return templates.TemplateResponse(
        request=request,
        name="admin/products/form.html",
        context={
            "title": f"Editar: {product.name} - Admin",
            "current_user": current_user,
            "product": product,
            "categories": categories,
        },
    )


# -----------------------------------------------------------------------------
# Categorias
# -----------------------------------------------------------------------------


@router.get("/categories", response_class=HTMLResponse)
async def list_categories(
    request: Request,
    current_user: AdminUser,
    repo: CategoryRepo,
    product_repo: ProductRepo,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
):
    """Listagem de categorias com paginacao e pesquisa."""
    skip = (page - 1) * per_page

    # Buscar categorias
    if q:
        categories = await repo.search(q, skip=skip, limit=per_page)
        total = await repo.count_search(q)
    else:
        categories = await repo.get_paginated(skip=skip, limit=per_page)
        total = await repo.count()

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    # Conta produtos por categoria (usando o slug)
    product_counts = {}
    for category in categories:
        product_counts[category.slug] = await product_repo.count_by_category(category.slug)

    return templates.TemplateResponse(
        request=request,
        name="admin/categories/list.html",
        context={
            "title": "Categorias - Admin",
            "current_user": current_user,
            "categories": categories,
            "product_counts": product_counts,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
            "q": q or "",
        },
    )


@router.get("/categories/new", response_class=HTMLResponse)
async def new_category(
    request: Request,
    current_user: AdminUser,
    repo: CategoryRepo,
):
    """Formulario de nova categoria."""
    categories = await repo.get_all()  # Para selecionar parent

    return templates.TemplateResponse(
        request=request,
        name="admin/categories/form.html",
        context={
            "title": "Nova Categoria - Admin",
            "current_user": current_user,
            "category": None,
            "categories": categories,
        },
    )


@router.get("/categories/{category_id}", response_class=HTMLResponse)
async def edit_category(
    request: Request,
    category_id: UUID,
    current_user: AdminUser,
    repo: CategoryRepo,
):
    """Formulario de edicao de categoria."""
    category = await repo.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    categories = await repo.get_all()  # Para selecionar parent

    return templates.TemplateResponse(
        request=request,
        name="admin/categories/form.html",
        context={
            "title": f"Editar: {category.name} - Admin",
            "current_user": current_user,
            "category": category,
            "categories": [c for c in categories if c.id != category.id],  # Excluir a propria
        },
    )


# -----------------------------------------------------------------------------
# Usuarios (apenas admin)
# -----------------------------------------------------------------------------


async def require_admin_role(
    current_user: AdminUser,
) -> User:
    """Requer role admin (nao editor)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user


@router.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: UserRepo,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
    role: Optional[str] = None,
):
    """Listagem de usuarios (apenas admin)."""
    skip = (page - 1) * per_page

    # Filtros
    filters = {}
    if role:
        try:
            filters["role"] = UserRole(role)
        except ValueError:
            pass

    # Buscar usuarios
    if q:
        users = await repo.search(q, skip=skip, limit=per_page)
        total = await repo.count_search(q)
    else:
        users = await repo.get_multi(skip=skip, limit=per_page, **filters)
        total = await repo.count(**filters)

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="admin/users/list.html",
        context={
            "title": "Usuarios - Admin",
            "current_user": current_user,
            "users": users,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        },
    )


@router.get("/users/new", response_class=HTMLResponse)
async def new_user(
    request: Request,
    current_user: Annotated[User, Depends(require_admin_role)],
):
    """Formulario de novo usuario (apenas admin)."""
    return templates.TemplateResponse(
        request=request,
        name="admin/users/form.html",
        context={
            "title": "Novo Usuario - Admin",
            "current_user": current_user,
            "user": None,
        },
    )


@router.get("/users/{user_id}", response_class=HTMLResponse)
async def edit_user(
    request: Request,
    user_id: UUID,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: UserRepo,
):
    """Formulario de edicao de usuario (apenas admin)."""
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    return templates.TemplateResponse(
        request=request,
        name="admin/users/form.html",
        context={
            "title": f"Editar: {user.name} - Admin",
            "current_user": current_user,
            "user": user,
        },
    )


# -----------------------------------------------------------------------------
# Ocasioes
# -----------------------------------------------------------------------------


@router.get("/occasions", response_class=HTMLResponse)
async def list_occasions(
    request: Request,
    current_user: AdminUser,
    repo: OccasionRepo,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
):
    """Listagem de ocasioes."""
    skip = (page - 1) * per_page

    # Buscar ocasioes
    if q:
        occasions = await repo.search(q, skip=skip, limit=per_page)
        total = await repo.count_search(q)
    else:
        occasions = await repo.get_paginated(skip=skip, limit=per_page)
        total = await repo.count()

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="admin/occasions/list.html",
        context={
            "title": "Ocasioes - Admin",
            "current_user": current_user,
            "occasions": occasions,
            "q": q,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        },
    )


@router.get("/occasions/new", response_class=HTMLResponse)
async def new_occasion(
    request: Request,
    current_user: AdminUser,
    product_repo: ProductRepo,
):
    """Formulario de nova ocasiao."""
    # Busca produtos para o modal de insercao
    products = await product_repo.get_all_active()

    return templates.TemplateResponse(
        request=request,
        name="admin/occasions/form.html",
        context={
            "title": "Nova Ocasiao - Admin",
            "current_user": current_user,
            "occasion": None,
            "products": products,
        },
    )


@router.get("/occasions/{occasion_id}", response_class=HTMLResponse)
async def edit_occasion(
    request: Request,
    occasion_id: UUID,
    current_user: AdminUser,
    repo: OccasionRepo,
    product_repo: ProductRepo,
):
    """Formulario de edicao de ocasiao."""
    occasion = await repo.get(occasion_id)
    if not occasion:
        raise HTTPException(status_code=404, detail="Ocasiao nao encontrada")

    # Busca produtos para o modal de insercao
    products = await product_repo.get_all_active()

    return templates.TemplateResponse(
        request=request,
        name="admin/occasions/form.html",
        context={
            "title": f"Editar: {occasion.name} - Admin",
            "current_user": current_user,
            "occasion": occasion,
            "products": products,
        },
    )


# -----------------------------------------------------------------------------
# Configuracoes de IA (apenas admin)
# -----------------------------------------------------------------------------


@router.get("/ai-configs", response_class=HTMLResponse)
async def list_ai_configs(
    request: Request,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: AIConfigRepo,
):
    """Listagem de configuracoes de IA."""
    configs = await repo.get_all()

    return templates.TemplateResponse(
        request=request,
        name="admin/ai-configs/list.html",
        context={
            "title": "Configuracoes de IA - Admin",
            "current_user": current_user,
            "configs": configs,
            "active_page": "ai-configs",
        },
    )


@router.get("/ai-configs/{config_id}", response_class=HTMLResponse)
async def edit_ai_config(
    request: Request,
    config_id: UUID,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: AIConfigRepo,
):
    """Formulario de edicao de configuracao de IA."""
    config = await repo.get(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuracao nao encontrada")

    return templates.TemplateResponse(
        request=request,
        name="admin/ai-configs/form.html",
        context={
            "title": f"Editar: {config.name} - Admin",
            "current_user": current_user,
            "config": config,
            "active_page": "ai-configs",
        },
    )


@router.post("/ai-configs/{config_id}", response_class=HTMLResponse)
async def update_ai_config(
    request: Request,
    config_id: UUID,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: AIConfigRepo,
    name: str = Form(...),
    description: str = Form(None),
    provider: str = Form(...),
    model: str = Form(...),
    system_prompt: str = Form(...),
    temperature: float = Form(0.7),
    max_tokens: int = Form(500),
    is_active: str = Form(None),
):
    """Atualiza configuracao de IA."""
    config = await repo.get(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuracao nao encontrada")

    # Atualiza campos
    update_data = {
        "name": name,
        "description": description or None,
        "provider": provider,
        "model": model,
        "system_prompt": system_prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "is_active": is_active == "true",
    }

    await repo.update(config, update_data)

    # Redireciona para a lista com mensagem de sucesso
    return RedirectResponse(
        url="/admin/ai-configs",
        status_code=status.HTTP_303_SEE_OTHER,
    )
