"""
Router para servir imagens Open Graph dinamicas.

Gera imagens 1200x630px otimizadas para compartilhamento em redes sociais.
As imagens sao cacheadas em disco para performance.
"""

from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi.responses import Response

from app.services.og_image import generate_og_image

router = APIRouter(prefix="/og", tags=["og-images"])


# -----------------------------------------------------------------------------
# Endpoints de Imagem OG
# -----------------------------------------------------------------------------


@router.get(
    "/post.png",
    response_class=Response,
    summary="Gera imagem OG para posts",
    responses={
        200: {"content": {"image/png": {}}, "description": "Imagem PNG gerada"},
    },
)
async def og_image_post(
    title: str = Query(..., min_length=1, max_length=200, description="Titulo do post"),
    subtitle: str | None = Query(None, max_length=300, description="Subtitulo ou resumo"),
    category: str | None = Query(None, max_length=100, description="Nome da categoria"),
):
    """
    Gera imagem Open Graph para posts do blog.

    A imagem e cacheada baseada no conteudo (titulo + subtitulo).
    Use como: /og/post.png?title=Meu+Post&subtitle=Resumo&category=Games
    """
    try:
        image_bytes = generate_og_image(
            title=title,
            og_type="post",
            subtitle=subtitle,
            category=category,
        )
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache 24h
                "Content-Disposition": "inline",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar imagem: {str(e)}",
        )


@router.get(
    "/product.png",
    response_class=Response,
    summary="Gera imagem OG para produtos",
    responses={
        200: {"content": {"image/png": {}}, "description": "Imagem PNG gerada"},
    },
)
async def og_image_product(
    title: str = Query(..., min_length=1, max_length=200, description="Nome do produto"),
    price: str | None = Query(None, max_length=50, description="Preco formatado (ex: R$ 99,90)"),
    platform: str | None = Query(None, max_length=50, description="Plataforma (amazon, mercadolivre, shopee)"),
):
    """
    Gera imagem Open Graph para produtos.

    A imagem e cacheada baseada no conteudo (nome + preco).
    Use como: /og/product.png?title=Produto&price=R$+99,90&platform=amazon
    """
    try:
        image_bytes = generate_og_image(
            title=title,
            og_type="product",
            price=price,
            platform=platform,
        )
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache 24h
                "Content-Disposition": "inline",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar imagem: {str(e)}",
        )


@router.get(
    "/category.png",
    response_class=Response,
    summary="Gera imagem OG para categorias",
    responses={
        200: {"content": {"image/png": {}}, "description": "Imagem PNG gerada"},
    },
)
async def og_image_category(
    title: str = Query(..., min_length=1, max_length=200, description="Nome da categoria"),
    subtitle: str | None = Query(None, max_length=300, description="Descricao da categoria"),
):
    """
    Gera imagem Open Graph para paginas de categoria.

    A imagem e cacheada baseada no conteudo (nome + descricao).
    Use como: /og/category.png?title=Games&subtitle=Os+melhores+jogos
    """
    try:
        image_bytes = generate_og_image(
            title=title,
            og_type="category",
            subtitle=subtitle,
        )
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache 24h
                "Content-Disposition": "inline",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar imagem: {str(e)}",
        )


@router.get(
    "/home.png",
    response_class=Response,
    summary="Gera imagem OG para homepage",
    responses={
        200: {"content": {"image/png": {}}, "description": "Imagem PNG gerada"},
    },
)
async def og_image_home():
    """
    Gera imagem Open Graph para a homepage.

    Imagem estatica cacheada para a pagina principal.
    """
    try:
        image_bytes = generate_og_image(
            title="geek.bidu.guru",
            og_type="home",
            subtitle="Presentes Geek - Encontre o presente perfeito",
        )
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=604800",  # Cache 7 dias
                "Content-Disposition": "inline",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar imagem: {str(e)}",
        )
