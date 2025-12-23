"""
Repositorios para acesso ao banco de dados.

Padrao Repository: abstrai operacoes de banco das rotas/services.
"""

from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.category import CategoryRepository
from app.repositories.occasion import OccasionRepository
from app.repositories.post import PostRepository
from app.repositories.product import ProductRepository
from app.repositories.click import ClickRepository
from app.repositories.session import SessionRepository
from app.repositories.newsletter import NewsletterRepository
from app.repositories.ai_config import AIConfigRepository
from app.repositories.social_integration import SocialIntegrationRepository
from app.repositories.price_history import PriceHistoryRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "CategoryRepository",
    "OccasionRepository",
    "PostRepository",
    "ProductRepository",
    "ClickRepository",
    "SessionRepository",
    "NewsletterRepository",
    "AIConfigRepository",
    "SocialIntegrationRepository",
    "PriceHistoryRepository",
]
