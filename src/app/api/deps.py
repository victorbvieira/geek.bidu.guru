"""
Dependências compartilhadas para endpoints da API.

Este módulo centraliza todas as dependências injetáveis da API, seguindo o
padrão de Injeção de Dependências (Dependency Injection) do FastAPI.

Princípios SOLID aplicados:
    - Single Responsibility: Cada função factory cria um único tipo de dependência
    - Dependency Inversion: Endpoints dependem de abstrações (type aliases)
    - Interface Segregation: Dependências específicas para cada domínio

Benefícios da centralização:
    - Facilita testes (mock de dependências)
    - Evita duplicação de código nos endpoints
    - Permite mudanças globais em um único lugar
    - Melhora a legibilidade dos endpoints

Uso nos endpoints:
    @router.get("/users")
    async def list_users(repo: UserRepo, pagination: Pagination):
        users = await repo.get_multi(**pagination)
        return users

Notas:
    - Todas as funções factory são assíncronas para compatibilidade
    - Type aliases (UserRepo, etc.) incluem a injeção automática
    - A sessão do banco é automaticamente fechada após cada request
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories import (
    AIConfigRepository,
    CategoryRepository,
    ClickRepository,
    NewsletterRepository,
    OccasionRepository,
    PostRepository,
    ProductRepository,
    SessionRepository,
    UserRepository,
)

# =============================================================================
# Sessão do Banco de Dados
# =============================================================================

# Type alias para injeção da sessão assíncrona do banco
# Uso: async def endpoint(db: DBSession) -> ...
DBSession = Annotated[AsyncSession, Depends(get_db)]


# =============================================================================
# Repositórios como Dependências
# =============================================================================
# Cada função factory cria uma instância do repositório com a sessão injetada.
# Isso permite:
#   1. Injeção automática da sessão do banco
#   2. Fácil substituição em testes (mock)
#   3. Escopo de vida gerenciado pelo FastAPI


async def get_user_repo(db: DBSession) -> UserRepository:
    """
    Factory para repositório de usuários.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do UserRepository pronta para uso
    """
    return UserRepository(db)


async def get_category_repo(db: DBSession) -> CategoryRepository:
    """
    Factory para repositório de categorias.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do CategoryRepository pronta para uso
    """
    return CategoryRepository(db)


async def get_post_repo(db: DBSession) -> PostRepository:
    """
    Factory para repositório de posts.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do PostRepository pronta para uso
    """
    return PostRepository(db)


async def get_product_repo(db: DBSession) -> ProductRepository:
    """
    Factory para repositório de produtos.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do ProductRepository pronta para uso
    """
    return ProductRepository(db)


async def get_click_repo(db: DBSession) -> ClickRepository:
    """
    Factory para repositório de cliques de afiliados.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do ClickRepository pronta para uso
    """
    return ClickRepository(db)


async def get_session_repo(db: DBSession) -> SessionRepository:
    """
    Factory para repositório de sessões de usuário.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do SessionRepository pronta para uso
    """
    return SessionRepository(db)


async def get_newsletter_repo(db: DBSession) -> NewsletterRepository:
    """
    Factory para repositório de newsletter.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do NewsletterRepository pronta para uso
    """
    return NewsletterRepository(db)


async def get_occasion_repo(db: DBSession) -> OccasionRepository:
    """
    Factory para repositório de ocasiões.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do OccasionRepository pronta para uso
    """
    return OccasionRepository(db)


async def get_ai_config_repo(db: DBSession) -> AIConfigRepository:
    """
    Factory para repositório de configuracoes de IA.

    Args:
        db: Sessão do banco injetada automaticamente

    Returns:
        Instância do AIConfigRepository pronta para uso
    """
    return AIConfigRepository(db)


# =============================================================================
# Type Aliases para Injeção Automática
# =============================================================================
# Estes aliases combinam o tipo do repositório com a injeção automática.
# Uso: async def endpoint(repo: UserRepo) -> ...
# O FastAPI automaticamente:
#   1. Obtém a sessão do banco via get_db
#   2. Cria o repositório via função factory
#   3. Injeta o repositório no endpoint

UserRepo = Annotated[UserRepository, Depends(get_user_repo)]
CategoryRepo = Annotated[CategoryRepository, Depends(get_category_repo)]
OccasionRepo = Annotated[OccasionRepository, Depends(get_occasion_repo)]
PostRepo = Annotated[PostRepository, Depends(get_post_repo)]
ProductRepo = Annotated[ProductRepository, Depends(get_product_repo)]
ClickRepo = Annotated[ClickRepository, Depends(get_click_repo)]
SessionRepo = Annotated[SessionRepository, Depends(get_session_repo)]
NewsletterRepo = Annotated[NewsletterRepository, Depends(get_newsletter_repo)]
AIConfigRepo = Annotated[AIConfigRepository, Depends(get_ai_config_repo)]


# =============================================================================
# Paginação
# =============================================================================


def pagination_params(
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """
    Processa e valida parâmetros de paginação da query string.

    Implementa proteções contra valores inválidos e limita o tamanho
    máximo da página para evitar sobrecarga do banco de dados.

    Args:
        page: Número da página (1-indexed). Default: 1
              Valores < 1 são corrigidos para 1
        per_page: Itens por página. Default: 20
                  Valores < 1 são corrigidos para 1
                  Valores > 100 são limitados a 100

    Returns:
        Dicionário com parâmetros processados:
        - skip: Offset para a query (calculado automaticamente)
        - limit: Número de registros a retornar
        - page: Número da página (corrigido se necessário)
        - per_page: Itens por página (corrigido se necessário)

    Exemplo de uso no endpoint:
        @router.get("/items")
        async def list_items(pagination: Pagination):
            items = await repo.get_multi(
                skip=pagination["skip"],
                limit=pagination["limit"]
            )
            return PaginatedResponse.create(
                items=items,
                page=pagination["page"],
                per_page=pagination["per_page"]
            )

    Notas:
        - O limite máximo de 100 itens por página é uma proteção
          contra consultas muito pesadas
        - O offset é calculado como (page - 1) * per_page
    """
    # Correção de valores inválidos com limites seguros
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 1
    if per_page > 100:
        per_page = 100  # Limite máximo para proteção de performance

    return {
        "skip": (page - 1) * per_page,  # Offset para a query SQL
        "limit": per_page,               # Quantidade de registros
        "page": page,                    # Página atual (para resposta)
        "per_page": per_page,            # Itens por página (para resposta)
    }


# Type alias para injeção automática dos parâmetros de paginação
# Uso: async def endpoint(pagination: Pagination) -> ...
Pagination = Annotated[dict, Depends(pagination_params)]
