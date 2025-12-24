"""
Rotas SSR para painel administrativo.

Renderiza templates HTML para:
- Dashboard com metricas
- CRUD de posts, produtos, categorias e usuarios
- Login/logout do admin
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, Response, status
from sqlalchemy import func
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    AIConfigRepo,
    CategoryRepo,
    DBSession,
    NewsletterRepo,
    OccasionRepo,
    Pagination,
    PostRepo,
    ProductRepo,
    SocialIntegrationRepo,
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


# -----------------------------------------------------------------------------
# Atualizacao de Precos (pagina de manutencao rapida)
# IMPORTANTE: Esta rota deve vir ANTES de /products/{product_id}
# -----------------------------------------------------------------------------


@router.get("/products/prices", response_class=HTMLResponse)
async def price_update_page(
    request: Request,
    current_user: AdminUser,
    product_repo: ProductRepo,
    category_repo: CategoryRepo,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    platform: str = Query("amazon", alias="platform"),
    outdated_only: bool = Query(False, alias="outdated"),
):
    """
    Pagina de atualizacao rapida de precos de produtos.

    Permite filtrar por categoria, plataforma e mostrar apenas precos
    desatualizados (mais de 24 horas sem atualizacao).

    Args:
        category: Slug da categoria para filtrar
        platform: Plataforma (amazon, mercadolivre, shopee) - padrao: amazon
        outdated_only: Se True, mostra apenas produtos com preco desatualizado
    """
    from datetime import timedelta, UTC, timezone
    from sqlalchemy import select, or_, cast
    from sqlalchemy.dialects.postgresql import JSONB
    from app.models import Product
    from app.models.product import ProductPlatform, ProductAvailability

    skip = (page - 1) * per_page

    # Mapeia string para enum de plataforma
    platform_map = {
        "amazon": ProductPlatform.AMAZON,
        "mercadolivre": ProductPlatform.MERCADOLIVRE,
        "shopee": ProductPlatform.SHOPEE,
    }
    selected_platform = platform_map.get(platform.lower(), ProductPlatform.AMAZON)

    # Query base - filtra por plataforma e disponibilidade
    query = (
        select(Product)
        .where(Product.platform == selected_platform)
        .where(Product.availability == ProductAvailability.AVAILABLE)
    )

    # Filtro por categoria
    if category:
        category_json = cast([category], JSONB)
        query = query.where(Product.categories.op("@>")(category_json))

    # Filtro de precos desatualizados (mais de 24 horas)
    if outdated_only:
        cutoff_time = datetime.now(UTC) - timedelta(hours=24)
        query = query.where(
            or_(
                Product.last_price_update.is_(None),
                Product.last_price_update < cutoff_time,
            )
        )

    # Conta total antes de paginar
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Aplica ordenacao e paginacao
    query = (
        query
        .order_by(Product.last_price_update.asc().nulls_first(), Product.name.asc())
        .offset(skip)
        .limit(per_page)
    )

    result = await db.execute(query)
    products = list(result.scalars().all())

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    # Busca categorias para o filtro
    categories = await category_repo.get_all()

    # Conta produtos com preco desatualizado para a plataforma selecionada
    cutoff_time = datetime.now(UTC) - timedelta(hours=24)
    outdated_count_query = (
        select(func.count())
        .select_from(Product)
        .where(Product.platform == selected_platform)
        .where(Product.availability == ProductAvailability.AVAILABLE)
        .where(
            or_(
                Product.last_price_update.is_(None),
                Product.last_price_update < cutoff_time,
            )
        )
    )
    if category:
        category_json = cast([category], JSONB)
        outdated_count_query = outdated_count_query.where(
            Product.categories.op("@>")(category_json)
        )
    outdated_result = await db.execute(outdated_count_query)
    outdated_count = outdated_result.scalar_one()

    # Funcao now() para o template calcular tempo desde ultima atualizacao
    def now_utc():
        return datetime.now(timezone.utc)

    return templates.TemplateResponse(
        request=request,
        name="admin/products/prices.html",
        context={
            "title": "Atualizar Precos - Admin",
            "current_user": current_user,
            "products": products,
            "categories": categories,
            "selected_category": category,
            "selected_platform": platform.lower(),
            "outdated_only": outdated_only,
            "outdated_count": outdated_count,
            "active_page": "products",
            "now": now_utc,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
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
    entity: str | None = None,
    use_case: str | None = None,
):
    """Listagem de configuracoes de IA com filtros opcionais."""
    configs = await repo.get_all()

    # Aplica filtros se fornecidos
    if entity:
        configs = [c for c in configs if c.entity and c.entity.value == entity]
    if use_case:
        configs = [c for c in configs if c.use_case and c.use_case.value == use_case]

    # Coleta valores unicos para os filtros
    from app.models.ai_config import AIEntity, AIUseCase
    entities = [e.value for e in AIEntity]
    use_cases = [uc.value for uc in AIUseCase]

    return templates.TemplateResponse(
        request=request,
        name="admin/ai-configs/list.html",
        context={
            "title": "Configuracoes de IA - Admin",
            "current_user": current_user,
            "configs": configs,
            "active_page": "ai-configs",
            "entities": entities,
            "use_cases": use_cases,
            "selected_entity": entity,
            "selected_use_case": use_case,
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
    user_prompt: str = Form(None),
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
        "user_prompt": user_prompt or None,
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


# -----------------------------------------------------------------------------
# AI Logs (Historico de chamadas LLM)
# -----------------------------------------------------------------------------


@router.get("/ai-logs", response_class=HTMLResponse)
async def list_ai_logs(
    request: Request,
    current_user: Annotated[User, Depends(require_admin_role)],
    db: DBSession,
    use_case: str | None = None,
    success: str | None = None,
):
    """
    Listagem de logs de chamadas ao LLM com filtros.

    Args:
        use_case: Filtra por caso de uso
        success: Filtra por status (1=sucesso, 0=erro)
    """
    from app.repositories.ai_log import AILogRepository
    from app.models.ai_config import AIUseCase

    repo = AILogRepository(db)

    # Converte success string para bool
    success_filter = None
    if success == "1":
        success_filter = True
    elif success == "0":
        success_filter = False

    # Busca logs com filtros
    logs = await repo.get_all(
        limit=50,
        use_case=use_case or None,
        success=success_filter,
    )

    # Estatisticas
    total_logs = await repo.count()
    success_count = await repo.count(success=True)
    error_count = await repo.count(success=False)
    total_cost = await repo.get_total_cost()

    # Lista de use_cases para o filtro
    use_cases = [uc.value for uc in AIUseCase]

    return templates.TemplateResponse(
        request=request,
        name="admin/ai-logs/list.html",
        context={
            "title": "Logs de IA - Admin",
            "current_user": current_user,
            "logs": logs,
            "active_page": "ai-logs",
            "use_cases": use_cases,
            "selected_use_case": use_case,
            "selected_success": success,
            "total_logs": total_logs,
            "success_count": success_count,
            "error_count": error_count,
            "total_cost": total_cost,
        },
    )


# -----------------------------------------------------------------------------
# Integracoes Sociais (apenas admin)
# -----------------------------------------------------------------------------


@router.get("/integrations", response_class=HTMLResponse)
async def list_integrations(
    request: Request,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: SocialIntegrationRepo,
):
    """
    Listagem de integracoes com redes sociais.

    Exibe todas as integracoes cadastradas (Instagram, etc.),
    permitindo visualizar o status e editar credenciais.
    """
    integrations = await repo.get_multi(order_by="platform", desc=False)

    return templates.TemplateResponse(
        request=request,
        name="admin/integrations/list.html",
        context={
            "title": "Integracoes - Admin",
            "current_user": current_user,
            "integrations": integrations,
            "active_page": "integrations",
        },
    )


@router.get("/integrations/{integration_id}", response_class=HTMLResponse)
async def edit_integration(
    request: Request,
    integration_id: UUID,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: SocialIntegrationRepo,
):
    """
    Formulario de edicao de integracao.

    Permite editar nome, user_id e token de acesso.
    O token atual e exibido apenas como preview (ofuscado).
    """
    integration = await repo.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integracao nao encontrada")

    return templates.TemplateResponse(
        request=request,
        name="admin/integrations/form.html",
        context={
            "title": f"Editar: {integration.name} - Admin",
            "current_user": current_user,
            "integration": integration,
            "active_page": "integrations",
        },
    )


@router.post("/integrations/{integration_id}", response_class=HTMLResponse)
async def update_integration(
    request: Request,
    integration_id: UUID,
    current_user: Annotated[User, Depends(require_admin_role)],
    repo: SocialIntegrationRepo,
    name: str = Form(...),
    platform_user_id: str = Form(None),
    access_token: str = Form(None),
    is_active: str = Form(None),
):
    """
    Atualiza integracao com rede social.

    Campos:
    - name: Nome identificador da integracao
    - platform_user_id: ID do usuario na plataforma (ex: IG_USER_ID)
    - access_token: Token de acesso a API (deixar vazio para manter o atual)
    - is_active: Se a integracao esta ativa
    """
    integration = await repo.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integracao nao encontrada")

    # Monta dados de atualizacao
    update_data = {
        "name": name,
        "platform_user_id": platform_user_id or None,
        "is_active": is_active == "true",
    }

    # So atualiza o token se foi fornecido um valor nao vazio
    # Isso evita apagar o token existente acidentalmente
    if access_token and access_token.strip():
        update_data["access_token"] = access_token.strip()

    await repo.update(integration, update_data)

    # Redireciona para a lista com mensagem de sucesso
    return RedirectResponse(
        url="/admin/integrations",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# -----------------------------------------------------------------------------
# Newsletter (gerenciamento de inscritos)
# -----------------------------------------------------------------------------


@router.get("/newsletter", response_class=HTMLResponse)
async def list_newsletter(
    request: Request,
    current_user: AdminUser,
    repo: NewsletterRepo,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    q: Optional[str] = None,
    status_filter: Optional[str] = Query("verified", alias="status"),
):
    """
    Listagem de inscritos na newsletter com filtros.

    Filtros disponiveis:
    - q: Busca por email
    - status: verified (padrao), pending, unsubscribed, ou vazio para todos
    """
    skip = (page - 1) * per_page

    # Busca inscritos com filtros
    from sqlalchemy import select, and_, or_
    from app.models import NewsletterSignup

    query = select(NewsletterSignup)

    # Filtro de busca por email
    if q:
        query = query.where(NewsletterSignup.email.ilike(f"%{q}%"))

    # Filtro de status (verified é o padrao)
    if status_filter == "verified":
        query = query.where(
            and_(
                NewsletterSignup.is_active == True,  # noqa: E712
                NewsletterSignup.email_verified == True,  # noqa: E712
            )
        )
    elif status_filter == "pending":
        query = query.where(
            and_(
                NewsletterSignup.is_active == True,  # noqa: E712
                NewsletterSignup.email_verified == False,  # noqa: E712
            )
        )
    elif status_filter == "unsubscribed":
        query = query.where(NewsletterSignup.is_active == False)  # noqa: E712

    # Conta total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await repo.db.execute(count_query)
    total = total_result.scalar_one()

    # Aplica ordenacao e paginacao
    query = (
        query
        .order_by(NewsletterSignup.subscribed_at.desc())
        .offset(skip)
        .limit(per_page)
    )

    result = await repo.db.execute(query)
    subscribers = list(result.scalars().all())

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    # Estatisticas
    stats = await repo.get_stats()

    return templates.TemplateResponse(
        request=request,
        name="admin/newsletter/list.html",
        context={
            "title": "Newsletter - Admin",
            "current_user": current_user,
            "subscribers": subscribers,
            "stats": stats,
            "active_page": "newsletter",
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        },
    )


@router.get("/newsletter/send", response_class=HTMLResponse)
async def send_newsletter_form(
    request: Request,
    current_user: AdminUser,
    repo: NewsletterRepo,
    selected_ids: list[str] = Query(None),
):
    """
    Formulario para envio de email em massa.

    Pode receber IDs pre-selecionados via query params.
    """
    from uuid import UUID

    # Conta verificados
    total_verified = await repo.count_verified()

    # Se tem IDs selecionados, busca os inscritos
    selected_subscribers = []
    if selected_ids:
        for sid in selected_ids:
            try:
                subscriber = await repo.get(UUID(sid))
                if subscriber and subscriber.is_active and subscriber.email_verified:
                    selected_subscribers.append(subscriber)
            except ValueError:
                pass

    return templates.TemplateResponse(
        request=request,
        name="admin/newsletter/send.html",
        context={
            "title": "Enviar Email - Admin",
            "current_user": current_user,
            "total_verified": total_verified,
            "selected_ids": selected_ids or [],
            "selected_subscribers": selected_subscribers,
            "current_year": datetime.now().year,
            "active_page": "newsletter",
        },
    )


@router.post("/newsletter/send", response_class=HTMLResponse)
async def send_newsletter_submit(
    request: Request,
    current_user: AdminUser,
    repo: NewsletterRepo,
    subject: str = Form(...),
    heading: str = Form(...),
    content: str = Form(""),
    preview_text: str = Form(None),
    cta_text: str = Form(None),
    cta_url: str = Form(None),
    recipient_type: str = Form("all"),
    selected_ids: list[str] = Form(None),
    test_email: str = Form(None),
    is_test: str = Form(None),
):
    """
    Processa envio de email em massa.

    Modos de envio:
    - is_test=true: Envia apenas para test_email
    - recipient_type=all: Envia para todos os verificados
    - recipient_type=selected: Envia para IDs selecionados
    """
    from uuid import UUID
    from app.services.email import email_service

    # Determina destinatarios
    recipients = []

    if is_test == "true" and test_email:
        # Modo teste: apenas um email
        recipients = [test_email]
    elif recipient_type == "all":
        # Todos os verificados
        verified = await repo.get_active_subscribers(limit=10000)
        recipients = [s.email for s in verified]
    elif recipient_type == "selected" and selected_ids:
        # Apenas selecionados
        for sid in selected_ids:
            try:
                subscriber = await repo.get(UUID(sid))
                if subscriber and subscriber.is_active and subscriber.email_verified:
                    recipients.append(subscriber.email)
            except ValueError:
                pass

    if not recipients:
        return templates.TemplateResponse(
            request=request,
            name="admin/newsletter/send.html",
            context={
                "title": "Enviar Email - Admin",
                "current_user": current_user,
                "total_verified": await repo.count_verified(),
                "selected_ids": [],
                "selected_subscribers": [],
                "current_year": datetime.now().year,
                "active_page": "newsletter",
                "error": "Nenhum destinatario encontrado.",
                "subject": subject,
                "heading": heading,
                "content": content,
                "preview_text": preview_text,
                "cta_text": cta_text,
                "cta_url": cta_url,
            },
        )

    # Envia emails
    success_count = 0
    error_count = 0

    for email_addr in recipients:
        try:
            sent = await email_service.send_newsletter_email(
                to_email=email_addr,
                subject=subject,
                heading=heading,
                content=content,
                preview_text=preview_text,
                cta_text=cta_text,
                cta_url=cta_url,
            )
            if sent:
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1

    # Mensagem de resultado
    if is_test == "true":
        message = f"Email de teste enviado para {test_email}!"
    else:
        message = f"Enviado com sucesso para {success_count} destinatario(s)."
        if error_count > 0:
            message += f" {error_count} erro(s)."

    return templates.TemplateResponse(
        request=request,
        name="admin/newsletter/send.html",
        context={
            "title": "Enviar Email - Admin",
            "current_user": current_user,
            "total_verified": await repo.count_verified(),
            "selected_ids": [],
            "selected_subscribers": [],
            "current_year": datetime.now().year,
            "active_page": "newsletter",
            "success": message,
        },
    )


@router.post("/newsletter/{subscriber_id}/resend")
async def resend_verification(
    subscriber_id: UUID,
    current_user: AdminUser,
    repo: NewsletterRepo,
):
    """Reenvia email de verificacao para um inscrito."""
    from app.config import settings
    from app.services.email import email_service

    subscriber = await repo.get(subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Inscrito nao encontrado")

    if subscriber.email_verified:
        return RedirectResponse(
            url="/admin/newsletter",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Gera novo token
    token = subscriber.generate_verification_token()
    await repo.db.commit()

    # Envia email
    verification_url = f"{settings.app_url}/api/v1/newsletter/verify/{token}"
    await email_service.send_verification_email(
        to_email=subscriber.email,
        verification_url=verification_url,
    )

    return RedirectResponse(
        url="/admin/newsletter",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/newsletter/{subscriber_id}/unsubscribe")
async def admin_unsubscribe(
    subscriber_id: UUID,
    current_user: AdminUser,
    repo: NewsletterRepo,
):
    """Desinscreve um inscrito via admin."""
    subscriber = await repo.get(subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Inscrito nao encontrado")

    await repo.unsubscribe(subscriber.email)

    return RedirectResponse(
        url="/admin/newsletter",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/newsletter/{subscriber_id}/resubscribe")
async def admin_resubscribe(
    subscriber_id: UUID,
    current_user: AdminUser,
    repo: NewsletterRepo,
):
    """Reinscreve um inscrito via admin."""
    subscriber = await repo.get(subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Inscrito nao encontrado")

    await repo.resubscribe(subscriber.email)

    return RedirectResponse(
        url="/admin/newsletter",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/newsletter/bulk-action")
async def bulk_action(
    request: Request,
    current_user: AdminUser,
    repo: NewsletterRepo,
    action: str = Form(...),
    selected_ids: list[str] = Form(None),
):
    """Executa acao em massa nos inscritos selecionados."""
    from uuid import UUID

    if not selected_ids:
        return RedirectResponse(
            url="/admin/newsletter",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    for sid in selected_ids:
        try:
            subscriber = await repo.get(UUID(sid))
            if not subscriber:
                continue

            if action == "unsubscribe":
                await repo.unsubscribe(subscriber.email)
            elif action == "delete":
                await repo.db.delete(subscriber)
        except ValueError:
            pass

    await repo.db.commit()

    return RedirectResponse(
        url="/admin/newsletter",
        status_code=status.HTTP_303_SEE_OTHER,
    )
