# Backend Developer (Python/FastAPI) - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: Backend Developer
**Área**: Técnica / Desenvolvimento
**Especialidade**: Python, FastAPI, APIs REST, lógica de negócio, server-side rendering (SSR)

## 🎯 Responsabilidades

- Desenvolvimento de APIs REST com FastAPI
- Implementação de lógica de negócio
- Server-side rendering com Jinja2
- Integração com banco de dados (PostgreSQL via SQLAlchemy)
- Autenticação e autorização
- Integração com APIs externas (Amazon, Mercado Livre, Shopee)
- Performance e otimização de queries
- Implementação de cache
- Testes unitários e de integração

## 🛠️ Stack Tecnológica

### Core
- **Python**: 3.11+
- **FastAPI**: Framework web moderno e rápido
- **Uvicorn**: ASGI server
- **Pydantic**: Validação de dados
- **SQLAlchemy**: ORM para PostgreSQL
- **Alembic**: Migrations de banco de dados
- **Jinja2**: Template engine para SSR

### Bibliotecas Auxiliares
- **httpx**: Cliente HTTP assíncrono
- **python-jose**: JWT tokens
- **passlib**: Hashing de senhas
- **python-multipart**: Upload de arquivos
- **python-slugify**: Geração de slugs
- **Pillow**: Processamento de imagens

### Desenvolvimento
- **pytest**: Testes
- **black**: Formatação de código
- **ruff**: Linting
- **mypy**: Type checking

## 📁 Estrutura do Projeto

```
geek-bidu-guru/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point do FastAPI
│   ├── config.py               # Configurações e env vars
│   ├── database.py             # Setup do SQLAlchemy
│   ├── dependencies.py         # Dependências injetáveis
│   │
│   ├── api/                    # Endpoints da API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── posts.py        # Endpoints de posts
│   │   │   ├── products.py     # Endpoints de produtos
│   │   │   ├── auth.py         # Autenticação
│   │   │   └── admin.py        # Endpoints admin
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── post.py
│   │   ├── product.py
│   │   ├── user.py
│   │   └── category.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── post.py
│   │   ├── product.py
│   │   └── user.py
│   │
│   ├── services/               # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── post_service.py
│   │   ├── product_service.py
│   │   ├── affiliate_service.py
│   │   └── seo_service.py
│   │
│   ├── routers/                # Rotas do site (SSR)
│   │   ├── __init__.py
│   │   ├── home.py
│   │   ├── post.py
│   │   ├── category.py
│   │   └── redirect.py         # /goto/{slug}
│   │
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── post.html
│   │   ├── category.html
│   │   └── components/
│   │       ├── header.html
│   │       ├── footer.html
│   │       └── product_card.html
│   │
│   ├── static/                 # CSS, JS, imagens
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   └── utils/                  # Utilitários
│       ├── __init__.py
│       ├── security.py         # Funções de segurança
│       ├── seo.py              # Helpers de SEO
│       └── cache.py            # Cache helpers
│
├── tests/
│   ├── __init__.py
│   ├── test_api/
│   ├── test_models/
│   └── test_services/
│
├── migrations/                 # Alembic migrations
│   └── versions/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🚀 Implementação - Exemplos

### 1. main.py - Setup do FastAPI

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import posts, products, auth
from app.routers import home, post, category, redirect
from app.database import engine, Base
from app.config import settings

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="geek.bidu.guru API",
    description="API para blog de presentes geek",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# API Routes (REST)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])

# Site Routes (SSR)
app.include_router(home.router, tags=["site"])
app.include_router(post.router, tags=["site"])
app.include_router(category.router, tags=["site"])
app.include_router(redirect.router, tags=["site"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

### 2. models/post.py - Modelo de Post

```python
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime
import enum

class PostType(str, enum.Enum):
    PRODUCT_SINGLE = "product_single"
    LISTICLE = "listicle"
    GUIDE = "guide"

class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(PostType), nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    subtitle = Column(String(300))
    content = Column(Text, nullable=False)
    featured_image_url = Column(String(500))

    # SEO
    seo_focus_keyword = Column(String(100))
    seo_title = Column(String(60))
    seo_description = Column(String(160))

    # Relacionamentos
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    category = relationship("Category", back_populates="posts")

    # Tags (JSONB array)
    tags = Column(JSONB, default=[])

    # Status
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    publish_at = Column(DateTime)
    shared = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com produtos
    products = relationship("Product", secondary="post_products", back_populates="posts")
```

---

### 3. schemas/post.py - Pydantic Schemas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.post import PostType, PostStatus
from slugify import slugify

class PostBase(BaseModel):
    type: PostType
    title: str = Field(..., min_length=10, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    content: str = Field(..., min_length=100)
    featured_image_url: Optional[str] = None
    category_id: UUID
    tags: List[str] = []
    seo_focus_keyword: Optional[str] = None
    seo_title: Optional[str] = Field(None, max_length=60)
    seo_description: Optional[str] = Field(None, max_length=160)

class PostCreate(PostBase):
    slug: Optional[str] = None

    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        if v:
            return slugify(v)
        if 'title' in values:
            return slugify(values['title'])
        return None

    @validator('seo_title', pre=True, always=True)
    def default_seo_title(cls, v, values):
        if v:
            return v
        if 'title' in values:
            return values['title'][:60]
        return None

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    subtitle: Optional[str] = None
    content: Optional[str] = None
    featured_image_url: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    seo_focus_keyword: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    status: Optional[PostStatus] = None

class PostResponse(PostBase):
    id: UUID
    slug: str
    status: PostStatus
    publish_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    shared: bool

    class Config:
        from_attributes = True
```

---

### 4. api/v1/posts.py - Endpoints de Posts

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.services import post_service
from app.dependencies import get_current_user, require_role
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "editor", "author"]))
):
    """Criar novo post"""
    return post_service.create_post(db, post_data, current_user.id)

@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    type: Optional[str] = None,
    category_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Listar posts com filtros"""
    return post_service.get_posts(
        db,
        skip=skip,
        limit=limit,
        status=status,
        type=type,
        category_id=category_id
    )

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID,
    db: Session = Depends(get_db)
):
    """Obter post por ID"""
    post = post_service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "editor"]))
):
    """Atualizar post"""
    post = post_service.update_post(db, post_id, post_data)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/{post_id}/publish", response_model=PostResponse)
async def publish_post(
    post_id: UUID,
    publish_at: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "editor"]))
):
    """Publicar post"""
    post = post_service.publish_post(db, post_id, publish_at)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Deletar post"""
    success = post_service.delete_post(db, post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
```

---

### 5. services/post_service.py - Lógica de Negócio

```python
from sqlalchemy.orm import Session
from app.models.post import Post, PostStatus
from app.schemas.post import PostCreate, PostUpdate
from datetime import datetime
from typing import Optional, List
from uuid import UUID

def create_post(db: Session, post_data: PostCreate, author_id: UUID) -> Post:
    """Criar novo post"""
    post = Post(
        **post_data.model_dump(),
        author_id=author_id
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    type: Optional[str] = None,
    category_id: Optional[UUID] = None
) -> List[Post]:
    """Listar posts com filtros"""
    query = db.query(Post)

    if status:
        query = query.filter(Post.status == status)
    if type:
        query = query.filter(Post.type == type)
    if category_id:
        query = query.filter(Post.category_id == category_id)

    return query.offset(skip).limit(limit).all()

def get_post_by_id(db: Session, post_id: UUID) -> Optional[Post]:
    """Obter post por ID"""
    return db.query(Post).filter(Post.id == post_id).first()

def get_post_by_slug(db: Session, slug: str) -> Optional[Post]:
    """Obter post por slug"""
    return db.query(Post).filter(Post.slug == slug).first()

def update_post(db: Session, post_id: UUID, post_data: PostUpdate) -> Optional[Post]:
    """Atualizar post"""
    post = get_post_by_id(db, post_id)
    if not post:
        return None

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    return post

def publish_post(db: Session, post_id: UUID, publish_at: Optional[datetime] = None) -> Optional[Post]:
    """Publicar post"""
    post = get_post_by_id(db, post_id)
    if not post:
        return None

    post.status = PostStatus.PUBLISHED
    post.publish_at = publish_at or datetime.utcnow()
    post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post_id: UUID) -> bool:
    """Deletar post"""
    post = get_post_by_id(db, post_id)
    if not post:
        return False

    db.delete(post)
    db.commit()
    return True
```

---

### 6. routers/post.py - Rota SSR de Post

```python
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import post_service, seo_service
from app.models.post import PostStatus

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/blog/{slug}", response_class=HTMLResponse)
async def post_page(
    request: Request,
    slug: str,
    db: Session = Depends(get_db)
):
    """Página de post individual"""
    post = post_service.get_post_by_slug(db, slug)

    if not post or post.status != PostStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Post not found")

    # SEO metadata
    seo_meta = seo_service.generate_post_seo(post)

    # Posts relacionados
    related_posts = post_service.get_related_posts(db, post, limit=3)

    return templates.TemplateResponse(
        "post.html",
        {
            "request": request,
            "post": post,
            "seo": seo_meta,
            "related_posts": related_posts
        }
    )
```

---

### 7. routers/redirect.py - Redirecionamento de Afiliados

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.services import affiliate_service

router = APIRouter()

@router.get("/goto/{affiliate_redirect_slug}")
async def affiliate_redirect(
    request: Request,
    affiliate_redirect_slug: str,
    db: Session = Depends(get_db)
):
    """Redirecionar para link de afiliado e registrar clique"""

    # Buscar produto pelo slug
    product = db.query(Product).filter(
        Product.affiliate_redirect_slug == affiliate_redirect_slug
    ).first()

    if not product or not product.affiliate_url_raw:
        raise HTTPException(status_code=404, detail="Product not found")

    # Registrar clique
    affiliate_service.track_click(
        db=db,
        product_id=product.id,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
        ip_address=request.client.host
    )

    # Redirecionar (302 = temporário)
    return RedirectResponse(
        url=product.affiliate_url_raw,
        status_code=302
    )
```

---

### 8. utils/security.py - Segurança

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash de senha com bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Criar JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decodificar JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
```

## ⚡ Performance e Otimização

### 1. Cache com Redis (opcional)

```python
from redis import asyncio as aioredis
import json

class Cache:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)

    async def get(self, key: str):
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: dict, ttl: int = 300):
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str):
        await self.redis.delete(key)

# Uso
cache = Cache("redis://localhost:6379")

@router.get("/blog/{slug}")
async def post_page(slug: str, db: Session = Depends(get_db)):
    # Tentar cache primeiro
    cached_post = await cache.get(f"post:{slug}")
    if cached_post:
        return cached_post

    # Buscar do banco
    post = post_service.get_post_by_slug(db, slug)

    # Salvar no cache (5 min)
    await cache.set(f"post:{slug}", post, ttl=300)

    return post
```

---

### 2. Paginação Eficiente

```python
from fastapi import Query
from sqlalchemy import func

@router.get("/api/v1/posts")
async def list_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Total de posts
    total = db.query(func.count(Post.id)).scalar()

    # Calcular offset
    skip = (page - 1) * per_page

    # Buscar posts
    posts = db.query(Post).offset(skip).limit(per_page).all()

    return {
        "data": posts,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
```

## 🧪 Testes

### Exemplo de Teste Unitário

```python
import pytest
from app.services import post_service
from app.schemas.post import PostCreate
from app.models.post import PostType

def test_create_post(db_session, test_user):
    """Testar criação de post"""
    post_data = PostCreate(
        type=PostType.PRODUCT_SINGLE,
        title="Teste de Post",
        content="Conteúdo do post de teste",
        category_id=test_category.id,
        tags=["teste", "exemplo"]
    )

    post = post_service.create_post(db_session, post_data, test_user.id)

    assert post.id is not None
    assert post.title == "Teste de Post"
    assert post.slug == "teste-de-post"
    assert post.author_id == test_user.id
```

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
