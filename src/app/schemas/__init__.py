"""
Pydantic schemas para validacao de dados.

Estrutura:
- base.py: Schemas base e utilitarios
- user.py: Usuarios e autenticacao
- category.py: Categorias de posts
- post.py: Posts/artigos
- product.py: Produtos de afiliados
- click.py: Tracking de cliques
- session.py: Tracking de sessoes
- newsletter.py: Inscricoes em newsletter
"""

# Base
from app.schemas.base import (
    BaseSchema,
    ErrorResponse,
    IDSchema,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
    ResponseSchema,
    TimestampSchema,
)

# User
from app.schemas.user import (
    TokenPayload,
    TokenResponse,
    UserBase,
    UserBrief,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    UserUpdatePassword,
)

# Category
from app.schemas.category import (
    CategoryBase,
    CategoryBrief,
    CategoryCreate,
    CategoryResponse,
    CategoryTree,
    CategoryUpdate,
    CategoryWithChildren,
)

# Post
from app.schemas.post import (
    PostBase,
    PostBrief,
    PostCreate,
    PostPublic,
    PostResponse,
    PostSEO,
    PostUpdate,
    PostUpdateStatus,
    PostWithRelations,
)

# Product
from app.schemas.product import (
    ProductAffiliate,
    ProductBase,
    ProductBrief,
    ProductCard,
    ProductCreate,
    ProductPublic,
    ProductResponse,
    ProductUpdate,
    ProductUpdatePrice,
    ProductUpdateScore,
)

# Click
from app.schemas.click import (
    ClickAnalytics,
    ClickBrief,
    ClickCreate,
    ClickResponse,
    ClicksByPeriod,
    ClicksByPost,
    ClicksByProduct,
    ClickStats,
)

# Session
from app.schemas.session import (
    SessionAnalytics,
    SessionBrief,
    SessionCreate,
    SessionResponse,
    SessionsByCountry,
    SessionsByDevice,
    SessionsByPost,
    SessionStats,
    SessionUpdate,
)

# Newsletter
from app.schemas.newsletter import (
    NewsletterBrief,
    NewsletterByPeriod,
    NewsletterBySource,
    NewsletterCreate,
    NewsletterPublicResponse,
    NewsletterResponse,
    NewsletterStats,
    NewsletterSubscribe,
    NewsletterUpdate,
)

__all__ = [
    # Base
    "BaseSchema",
    "TimestampSchema",
    "IDSchema",
    "ResponseSchema",
    "PaginationParams",
    "PaginatedResponse",
    "MessageResponse",
    "ErrorResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserUpdatePassword",
    "UserResponse",
    "UserBrief",
    "UserLogin",
    "TokenResponse",
    "TokenPayload",
    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryBrief",
    "CategoryWithChildren",
    "CategoryTree",
    # Post
    "PostBase",
    "PostSEO",
    "PostCreate",
    "PostUpdate",
    "PostUpdateStatus",
    "PostResponse",
    "PostWithRelations",
    "PostBrief",
    "PostPublic",
    # Product
    "ProductBase",
    "ProductAffiliate",
    "ProductCreate",
    "ProductUpdate",
    "ProductUpdatePrice",
    "ProductUpdateScore",
    "ProductResponse",
    "ProductBrief",
    "ProductPublic",
    "ProductCard",
    # Click
    "ClickCreate",
    "ClickResponse",
    "ClickBrief",
    "ClickStats",
    "ClicksByPeriod",
    "ClicksByProduct",
    "ClicksByPost",
    "ClickAnalytics",
    # Session
    "SessionCreate",
    "SessionUpdate",
    "SessionResponse",
    "SessionBrief",
    "SessionStats",
    "SessionsByDevice",
    "SessionsByCountry",
    "SessionsByPost",
    "SessionAnalytics",
    # Newsletter
    "NewsletterCreate",
    "NewsletterSubscribe",
    "NewsletterUpdate",
    "NewsletterResponse",
    "NewsletterBrief",
    "NewsletterPublicResponse",
    "NewsletterStats",
    "NewsletterBySource",
    "NewsletterByPeriod",
]
