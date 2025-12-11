"""
Router principal da API v1.

Agrupa todos os endpoints em um unico router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import categories, clicks, newsletter, posts, products, users

api_router = APIRouter()

# Registrar routers de cada modulo
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(posts.router)
api_router.include_router(products.router)
api_router.include_router(newsletter.router)
api_router.include_router(clicks.router)
