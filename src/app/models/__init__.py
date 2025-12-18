"""
Modelos SQLAlchemy para geek.bidu.guru.

Todos os modelos sao importados aqui para facilitar o uso
e para que o Alembic detecte automaticamente as mudancas.
"""

from app.models.base import JSONBType, TimestampMixin, UUIDMixin
from app.models.user import User
from app.models.category import Category
from app.models.occasion import Occasion
from app.models.post import Post, PostStatus, PostType
from app.models.product import Product, ProductPlatform, ProductAvailability
from app.models.post_product import PostProduct
from app.models.click import AffiliateClick
from app.models.session import Session
from app.models.newsletter import NewsletterSignup
from app.models.redirect import Redirect
from app.models.ai_config import AIConfig, AIProvider, AIUseCase
from app.models.instagram_post import InstagramPostHistory

__all__ = [
    # Mixins e Tipos
    "TimestampMixin",
    "UUIDMixin",
    "JSONBType",
    # Models
    "User",
    "Category",
    "Occasion",
    "Post",
    "PostStatus",
    "PostType",
    "Product",
    "ProductPlatform",
    "ProductAvailability",
    "PostProduct",
    "AffiliateClick",
    "Session",
    "NewsletterSignup",
    "Redirect",
    "AIConfig",
    "AIProvider",
    "AIUseCase",
    "InstagramPostHistory",
]
