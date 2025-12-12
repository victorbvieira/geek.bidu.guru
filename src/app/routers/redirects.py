"""
Rotas de Redirect 301 para URLs antigas.

Gerencia redirecionamentos permanentes de URLs legadas para as novas estruturas.
Util para migracao de blogs antigos ou mudancas de estrutura de URL.

Funcionalidades:
- Redirects estaticos (mapeamento exato)
- Redirects por padrao (prefixo de URL)
- Armazenamento em banco de dados (tabela redirects)
- Contador de hits para analytics
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.redirect import Redirect

router = APIRouter(tags=["redirects"])


# -----------------------------------------------------------------------------
# Redirects Estaticos (configuracao em codigo)
# -----------------------------------------------------------------------------

# Mapeamento estatico: "url_antiga" -> "url_nova"
# Use para redirects que nunca mudam ou migracao inicial
STATIC_REDIRECTS: dict[str, str] = {
    # Exemplos de redirecionamentos:
    # "artigo/meu-post-antigo": "/blog/meu-post-antigo",
    # "categoria-antiga/subcategoria": "/categoria/nova-categoria",
}

# Padroes de prefixo: (prefixo_antigo, prefixo_novo)
# Use para converter estruturas de URL inteiras
PATTERN_REDIRECTS: list[tuple[str, str]] = [
    # Exemplos de padroes:
    # ("artigo/", "/blog/"),        # /artigo/slug -> /blog/slug
    # ("post/", "/blog/"),          # /post/slug -> /blog/slug
    # ("category/", "/categoria/"), # /category/slug -> /categoria/slug
]


# -----------------------------------------------------------------------------
# Funcoes de Lookup
# -----------------------------------------------------------------------------


def _check_static_redirect(path: str) -> str | None:
    """Verifica redirect estatico (mapeamento exato)."""
    clean_path = path.lstrip("/")
    return STATIC_REDIRECTS.get(clean_path)


def _check_pattern_redirect(path: str) -> str | None:
    """Verifica redirect por padrao (prefixo)."""
    clean_path = path.lstrip("/")

    for old_prefix, new_prefix in PATTERN_REDIRECTS:
        if clean_path.startswith(old_prefix):
            slug = clean_path[len(old_prefix) :]
            return f"{new_prefix}{slug}"

    return None


async def _check_db_redirect(db: AsyncSession, path: str) -> Redirect | None:
    """Verifica redirect no banco de dados."""
    clean_path = path.lstrip("/")

    # 1. Busca match exato (nao e pattern)
    stmt = select(Redirect).where(
        Redirect.old_path == clean_path,
        Redirect.is_active == True,  # noqa: E712
        Redirect.is_pattern == False,  # noqa: E712
    )
    result = await db.execute(stmt)
    redirect = result.scalar_one_or_none()

    if redirect:
        return redirect

    # 2. Busca por patterns (prefixos)
    stmt = select(Redirect).where(
        Redirect.is_active == True,  # noqa: E712
        Redirect.is_pattern == True,  # noqa: E712
    )
    result = await db.execute(stmt)
    patterns = result.scalars().all()

    for pattern in patterns:
        if clean_path.startswith(pattern.old_path):
            # Retorna uma copia com o path ajustado
            slug = clean_path[len(pattern.old_path) :]
            pattern._computed_new_path = f"{pattern.new_path}{slug}"
            return pattern

    return None


async def _increment_hit_count(db: AsyncSession, redirect_id) -> None:
    """Incrementa contador de hits do redirect."""
    stmt = (
        update(Redirect)
        .where(Redirect.id == redirect_id)
        .values(hit_count=Redirect.hit_count + 1)
    )
    await db.execute(stmt)
    await db.commit()


# -----------------------------------------------------------------------------
# Endpoint de Redirect
# -----------------------------------------------------------------------------

# Nota: Este router NAO deve ser incluido no main.py com um prefix,
# pois ele usa catch-all path. Ao inves disso, use um middleware
# ou inclua como ultimo router.


async def check_redirect(
    path: str, request: Request, db: AsyncSession
) -> RedirectResponse | None:
    """
    Funcao utilitaria para verificar redirects.

    Pode ser chamada de um middleware ou exception handler.

    Returns:
        RedirectResponse se encontrou redirect, None caso contrario
    """
    # 1. Verifica estatico primeiro (mais rapido)
    new_url = _check_static_redirect(path)

    # 2. Verifica pattern estatico
    if not new_url:
        new_url = _check_pattern_redirect(path)

    # 3. Verifica no banco de dados
    redirect_obj = None
    if not new_url:
        redirect_obj = await _check_db_redirect(db, path)
        if redirect_obj:
            # Usa path computado se for pattern
            new_url = getattr(redirect_obj, "_computed_new_path", redirect_obj.new_path)

    if new_url:
        # Preserva query string
        query = str(request.query_params)
        if query:
            new_url = f"{new_url}?{query}"

        # Incrementa contador (fire and forget)
        if redirect_obj:
            try:
                await _increment_hit_count(db, redirect_obj.id)
            except Exception:
                pass  # Nao falha se o contador nao incrementar

        return RedirectResponse(url=new_url, status_code=301)

    return None


# -----------------------------------------------------------------------------
# API para listar redirects (debug/admin)
# -----------------------------------------------------------------------------


@router.get("/api/v1/admin/redirects")
async def list_all_redirects(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Lista todos os redirects configurados (estaticos e banco).

    Util para debug e administracao.
    """
    # Redirects estaticos
    static = [
        {"old_path": k, "new_path": v, "source": "static"}
        for k, v in STATIC_REDIRECTS.items()
    ]

    # Redirects por pattern estatico
    patterns = [
        {"old_prefix": old, "new_prefix": new, "source": "pattern"}
        for old, new in PATTERN_REDIRECTS
    ]

    # Redirects do banco
    stmt = select(Redirect).where(Redirect.is_active == True)  # noqa: E712
    result = await db.execute(stmt)
    db_redirects = result.scalars().all()

    database = [
        {
            "id": str(r.id),
            "old_path": r.old_path,
            "new_path": r.new_path,
            "is_pattern": r.is_pattern,
            "hit_count": r.hit_count,
            "source": "database",
        }
        for r in db_redirects
    ]

    return {
        "static_redirects": static,
        "pattern_redirects": patterns,
        "database_redirects": database,
        "total": len(static) + len(patterns) + len(database),
    }
