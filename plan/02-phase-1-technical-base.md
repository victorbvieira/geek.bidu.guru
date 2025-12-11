# Fase 1: Base Tecnica

**Prioridade**: CRITICA
**Objetivo**: Infraestrutura funcional com MVP do blog
**Agentes Principais**: DevOps Engineer, Backend Developer, Database Architect, Frontend Developer, Security Engineer

---

## Visao Geral da Fase

A Fase 1 estabelece toda a fundacao tecnica do projeto. Ao final desta fase, teremos:
- Ambiente Docker completo e funcional
- Backend FastAPI com APIs REST
- Banco de dados PostgreSQL com schema completo
- Sistema de autenticacao JWT
- Templates Jinja2 basicos renderizados
- Sistema de redirecionamento de afiliados funcionando

---

## 1.1 Infraestrutura Docker

**Agente Principal**: DevOps Engineer
**Referencia**: `agents/devops-engineer.md`

### 1.1.1 Criar Dockerfile

**Arquivo**: `docker/Dockerfile`

```dockerfile
# Multi-stage build para producao otimizada
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias de build
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Imagem final
FROM python:3.11-slim

WORKDIR /app

# Instalar apenas runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels do builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copiar codigo fonte
COPY src/ ./src/

# Usuario nao-root para seguranca
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Variaveis de ambiente
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.1.2 Criar docker-compose.yml (Desenvolvimento)

**Arquivo**: `docker/docker-compose.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: geek_db
    environment:
      POSTGRES_USER: ${DB_USER:-geek}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-geek_secret}
      POSTGRES_DB: ${DB_NAME:-geek_bidu}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-geek}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: geek_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: geek_app
    environment:
      - DATABASE_URL=postgresql://${DB_USER:-geek}:${DB_PASSWORD:-geek_secret}@db:5432/${DB_NAME:-geek_bidu}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-dev-secret-key-change-in-production}
      - DEBUG=${DEBUG:-true}
    volumes:
      - ../src:/app/src:ro
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  nginx:
    image: nginx:alpine
    container_name: geek_nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ../src/app/static:/var/www/static:ro
    ports:
      - "80:80"
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

### 1.1.3-1.1.8 Demais Arquivos de Infraestrutura

**Verificar**: `agents/devops-engineer.md` para configuracoes detalhadas de:
- Nginx config
- docker-compose.prod.yml
- .env.example
- Makefile

---

## 1.2 Backend FastAPI - Estrutura Base

**Agente Principal**: Backend Developer
**Referencia**: `agents/backend-developer.md`

### 1.2.1 Estrutura de Pastas

Criar a seguinte estrutura em `src/`:

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── posts.py
│   │       ├── products.py
│   │       ├── auth.py
│   │       └── affiliates.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── product.py
│   │   └── analytics.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── product.py
│   │   └── auth.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── post_service.py
│   │   ├── product_service.py
│   │   └── affiliate_service.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── home.py
│   │   ├── post.py
│   │   └── category.py
│   ├── templates/
│   │   └── (templates Jinja2)
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── utils/
│       ├── __init__.py
│       ├── security.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
└── migrations/
    ├── alembic.ini
    ├── env.py
    └── versions/
```

### 1.2.2 main.py

**Arquivo**: `src/app/main.py`

```python
"""
Entry point da aplicacao FastAPI - geek.bidu.guru
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.api.v1 import posts, products, auth, affiliates
from app.routers import home, post, category

# Criar aplicacao FastAPI
app = FastAPI(
    title="geek.bidu.guru API",
    description="API do blog de presentes geek",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estaticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates Jinja2
templates = Jinja2Templates(directory="app/templates")

# Registrar rotas da API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(affiliates.router, prefix="/api/v1/affiliates", tags=["affiliates"])

# Registrar rotas SSR (site)
app.include_router(home.router, tags=["site"])
app.include_router(post.router, tags=["site"])
app.include_router(category.router, tags=["site"])


@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoramento."""
    return {"status": "healthy", "version": "1.0.0"}


@app.on_event("startup")
async def startup():
    """Executa na inicializacao da aplicacao."""
    # Inicializar conexao com banco
    pass


@app.on_event("shutdown")
async def shutdown():
    """Executa no encerramento da aplicacao."""
    # Fechar conexoes
    pass
```

### 1.2.3 config.py

**Arquivo**: `src/app/config.py`

```python
"""
Configuracoes da aplicacao usando Pydantic BaseSettings.
"""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuracoes da aplicacao."""

    # Aplicacao
    APP_NAME: str = "geek.bidu.guru"
    DEBUG: bool = False
    SECRET_KEY: str

    # Banco de dados
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Afiliados
    AMAZON_AFFILIATE_TAG: str = ""
    MERCADOLIVRE_AFFILIATE_ID: str = ""
    SHOPEE_AFFILIATE_ID: str = ""

    # Analytics
    GA4_MEASUREMENT_ID: str = ""

    # n8n
    N8N_WEBHOOK_SECRET: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada das configuracoes."""
    return Settings()


settings = get_settings()
```

### 1.2.4 database.py

**Arquivo**: `src/app/database.py`

```python
"""
Configuracao do banco de dados PostgreSQL com SQLAlchemy.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Criar engine async
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base para modelos
Base = declarative_base()


async def get_db():
    """Dependency que fornece sessao do banco."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 1.2.5 requirements.txt

**Arquivo**: `requirements.txt`

```
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Templates
jinja2==3.1.2

# Database
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.12.1

# Validation
pydantic==2.5.2
pydantic-settings==2.1.0
email-validator==2.1.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Cache
redis==5.0.1
aioredis==2.0.1

# HTTP Client
httpx==0.25.2

# Utils
python-slugify==8.0.1
python-dateutil==2.8.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Dev
black==23.11.0
ruff==0.1.6
mypy==1.7.1
```

---

## 1.3 Banco de Dados - Schema

**Agente Principal**: Database Architect
**Referencia**: `agents/database-architect.md`

### 1.3.1 Modelo User

**Arquivo**: `src/app/models/user.py`

```python
"""
Modelo de usuario do sistema.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
import enum


class UserRole(str, enum.Enum):
    """Roles disponiveis no sistema."""
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    AUTOMATION = "automation"


class User(Base):
    """Modelo de usuario."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.AUTHOR, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
```

### 1.3.2 Modelo Post

**Arquivo**: `src/app/models/post.py`

```python
"""
Modelo de post/artigo do blog.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class PostStatus(str, enum.Enum):
    """Status do post."""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class PostType(str, enum.Enum):
    """Tipo do post."""
    SINGLE_PRODUCT = "single_product"
    LISTICLE = "listicle"
    GUIDE = "guide"
    REVIEW = "review"


class Post(Base):
    """Modelo de post."""
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Conteudo
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    excerpt = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    featured_image = Column(String(500), nullable=True)

    # SEO
    meta_title = Column(String(60), nullable=True)
    meta_description = Column(String(160), nullable=True)
    keywords = Column(ARRAY(String), default=[])

    # Classificacao
    post_type = Column(Enum(PostType), default=PostType.SINGLE_PRODUCT)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT, index=True)

    # Relacionamentos
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)

    # Metricas
    view_count = Column(Integer, default=0)

    # Datas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True, index=True)

    # Relationships
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    products = relationship("PostProduct", back_populates="post")
```

### 1.3.3 Modelo Product

**Arquivo**: `src/app/models/product.py`

```python
"""
Modelo de produto para afiliados.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Text, Boolean, DateTime, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class Platform(str, enum.Enum):
    """Plataformas de afiliados."""
    AMAZON = "amazon"
    MERCADOLIVRE = "mercadolivre"
    SHOPEE = "shopee"


class Product(Base):
    """Modelo de produto."""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Informacoes basicas
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    # Preco e plataforma
    platform = Column(Enum(Platform), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=True)
    original_price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="BRL")

    # Links de afiliado
    affiliate_url = Column(String(1000), nullable=False)
    affiliate_redirect_slug = Column(String(100), unique=True, nullable=False, index=True)

    # Dados adicionais
    rating = Column(Numeric(2, 1), nullable=True)
    review_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)

    # Metadata da API
    external_id = Column(String(100), nullable=True, index=True)
    api_data = Column(JSONB, default={})

    # Datas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    price_updated_at = Column(DateTime, nullable=True)

    # Relationships
    posts = relationship("PostProduct", back_populates="product")
    clicks = relationship("AffiliateClick", back_populates="product")
```

### 1.3.4 - 1.3.10 Demais Modelos

Consultar `agents/database-architect.md` para implementacao completa de:
- PostProduct (N:N)
- Category
- AffiliateClick
- Session
- NewsletterSignup
- Indices e migrations

---

## 1.4 Backend - Autenticacao

**Agente Principal**: Security Engineer + Backend Developer
**Referencia**: `agents/security-engineer.md`, `agents/backend-developer.md`

### 1.4.1 utils/security.py

```python
"""
Utilitarios de seguranca: hashing e JWT.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash bcrypt da senha."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Cria JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decodifica e valida JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

## 1.5-1.6 Backend - CRUD Posts e Products

**Agente Principal**: Backend Developer
**Referencia**: `agents/backend-developer.md`

Consultar o agente para implementacao completa de:
- Pydantic schemas
- Services com business logic
- Endpoints REST CRUD
- Paginacao e filtros

---

## 1.7 Backend - Sistema de Afiliados

**Agente Principal**: Affiliate Marketing Specialist + Backend Developer
**Referencia**: `agents/affiliate-marketing-specialist.md`

### Endpoint de Redirecionamento

**Arquivo**: `src/app/api/v1/affiliates.py`

```python
"""
Endpoints para sistema de afiliados.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.affiliate_service import AffiliateService

router = APIRouter()


@router.get("/goto/{slug}")
async def redirect_to_affiliate(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Redireciona para o link de afiliado e registra o clique.

    Este endpoint:
    1. Busca o produto pelo slug de redirecionamento
    2. Registra o clique na tabela affiliate_clicks
    3. Redireciona (HTTP 302) para a URL do afiliado
    """
    service = AffiliateService(db)

    # Buscar produto
    product = await service.get_product_by_redirect_slug(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    # Registrar clique
    await service.track_click(
        product_id=product.id,
        # Capturar request info para analytics
    )

    # Redirecionar
    return RedirectResponse(url=product.affiliate_url, status_code=302)
```

---

## 1.8-1.9 Frontend - Templates e Rotas SSR

**Agente Principal**: Frontend Developer + UX/UI Designer
**Referencia**: `agents/frontend-developer.md`, `agents/ux-ui-designer.md`

### Template Base

**Arquivo**: `src/app/templates/base.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO -->
    <title>{% block title %}geek.bidu.guru{% endblock %}</title>
    <meta name="description" content="{% block meta_description %}Curadoria de presentes geek perfeitos para todas as ocasioes{% endblock %}">

    <!-- Open Graph -->
    <meta property="og:title" content="{% block og_title %}{{ self.title() }}{% endblock %}">
    <meta property="og:description" content="{% block og_description %}{{ self.meta_description() }}{% endblock %}">
    <meta property="og:image" content="{% block og_image %}/static/images/og-default.jpg{% endblock %}">
    <meta property="og:type" content="{% block og_type %}website{% endblock %}">

    <!-- Favicon -->
    <link rel="icon" href="/static/images/favicon.ico">

    <!-- CSS -->
    <link rel="stylesheet" href="/static/css/main.css">
    {% block extra_css %}{% endblock %}
</head>
<body class="dark-theme">
    <!-- Skip to content -->
    <a href="#main-content" class="skip-link">Pular para conteudo principal</a>

    <!-- Header -->
    {% include "components/header.html" %}

    <!-- Main Content -->
    <main id="main-content">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    {% include "components/footer.html" %}

    <!-- JavaScript -->
    <script src="/static/js/main.js"></script>
    {% block extra_js %}{% endblock %}

    <!-- Analytics (GA4) -->
    {% if config.GA4_MEASUREMENT_ID %}
    <script async src="https://www.googletagmanager.com/gtag/js?id={{ config.GA4_MEASUREMENT_ID }}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '{{ config.GA4_MEASUREMENT_ID }}');
    </script>
    {% endif %}
</body>
</html>
```

---

## 1.10 Seguranca Base

**Agente Principal**: Security Engineer
**Referencia**: `agents/security-engineer.md`

### Checklist OWASP Top 10 (Fase 1)

| Vulnerabilidade | Mitigacao | Status |
|-----------------|-----------|--------|
| A01 - Broken Access Control | RBAC com roles, JWT validation | :white_large_square: |
| A02 - Cryptographic Failures | bcrypt para senhas, HTTPS, secrets em .env | :white_large_square: |
| A03 - Injection | SQLAlchemy ORM (parametrized), Pydantic validation | :white_large_square: |
| A04 - Insecure Design | Principio do menor privilegio, validacao de entrada | :white_large_square: |
| A05 - Security Misconfiguration | CORS restrito, headers de seguranca, DEBUG=False em prod | :white_large_square: |
| A06 - Vulnerable Components | requirements.txt com versoes fixas, updates regulares | :white_large_square: |
| A07 - Auth Failures | JWT com expiracao, rate limiting em login | :white_large_square: |
| A08 - Data Integrity | Validacao Pydantic, sanitizacao de input | :white_large_square: |
| A09 - Logging Failures | Logging estruturado (implementar na Fase 4) | :white_large_square: |
| A10 - SSRF | Validacao de URLs externas | :white_large_square: |

---

## Criterios de Conclusao da Fase 1

- [ ] Docker Compose sobe todos os servicos sem erros
- [ ] API responde em `http://localhost:8000/api/docs`
- [ ] Banco de dados criado com todas as tabelas
- [ ] Usuario admin pode fazer login via JWT
- [ ] CRUD de posts funciona via API
- [ ] CRUD de produtos funciona via API
- [ ] Homepage renderiza com template Jinja2
- [ ] Pagina de post renderiza corretamente
- [ ] Sistema de redirect `/goto/{slug}` funciona
- [ ] Testes unitarios basicos passando
- [ ] Nenhum secret exposto no codigo

---

## Proxima Fase

Apos concluir a Fase 1, avance para:
- **Fase 2**: SEO & Automacao (`03-phase-2-seo-automation.md`)

---

**Versao**: 1.0
**Data**: 2025-12-10
**Projeto**: geek.bidu.guru
