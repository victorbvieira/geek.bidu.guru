"""
Endpoints REST para gerenciamento de Usuários.

Este módulo implementa as operações CRUD completas para usuários do sistema
administrativo (admin, editor, author, automation).

Endpoints disponíveis:
    GET    /users           - Lista usuários com paginação
    GET    /users/{id}      - Busca usuário por ID
    POST   /users           - Cria novo usuário
    PATCH  /users/{id}      - Atualiza usuário existente
    DELETE /users/{id}      - Remove usuário

Segurança:
    - Senhas são hasheadas com bcrypt antes de persistir
    - Emails são validados como únicos
    - Endpoints de escrita podem ser protegidos com JWT (ver exemplo em delete)

Notas:
    - Todos os endpoints são assíncronos para melhor performance
    - Utiliza injeção de dependências para repositório e paginação
    - Retorna respostas padronizadas via Pydantic schemas

Protecao de Endpoints:
    Para proteger um endpoint, adicione a dependencia require_role ou ActiveUser:

    from app.core.deps import ActiveUser, require_role
    from app.models.user import UserRole

    # Qualquer usuario autenticado:
    @router.get("/protected")
    async def protected_route(current_user: ActiveUser):
        return {"user": current_user.email}

    # Apenas admin:
    @router.delete("/{id}", dependencies=[Depends(require_role(UserRole.ADMIN))])
    async def admin_only(id: UUID):
        ...

    # Admin ou Editor:
    @router.patch("/{id}", dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.EDITOR))])
    async def admin_or_editor(id: UUID):
        ...
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.hash import bcrypt

from app.api.deps import Pagination, UserRepo
from app.core.deps import require_role
from app.models.user import UserRole
from app.schemas import (
    MessageResponse,
    PaginatedResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

# Router com prefixo /users e tag para documentação OpenAPI
router = APIRouter(prefix="/users", tags=["users"])


# =============================================================================
# Endpoints de Leitura (GET)
# =============================================================================


@router.get("", response_model=PaginatedResponse)
async def list_users(
    repo: UserRepo,
    pagination: Pagination,
):
    """
    Lista todos os usuários com paginação.

    Retorna uma lista paginada de usuários, ordenados por data de criação
    (mais recentes primeiro).

    Args:
        repo: Repositório de usuários (injetado automaticamente)
        pagination: Parâmetros de paginação da query string

    Returns:
        PaginatedResponse contendo:
        - items: Lista de usuários (UserResponse)
        - total: Total de usuários no banco
        - page: Página atual
        - per_page: Itens por página
        - pages: Total de páginas

    Query Parameters:
        page (int): Número da página (default: 1)
        per_page (int): Itens por página (default: 20, max: 100)

    Exemplo de resposta:
        {
            "items": [{"id": "...", "name": "João", ...}],
            "total": 50,
            "page": 1,
            "per_page": 20,
            "pages": 3
        }
    """
    # Busca usuários com paginação, ordenados por data de criação
    users = await repo.get_multi(
        skip=pagination["skip"],
        limit=pagination["limit"],
        order_by="created_at",  # Mais recentes primeiro (desc=True é default)
    )

    # Conta total para calcular páginas
    total = await repo.count()

    # Monta resposta paginada convertendo models para schemas
    return PaginatedResponse.create(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, repo: UserRepo):
    """
    Busca um usuário específico por seu ID.

    Args:
        user_id: UUID do usuário a ser buscado
        repo: Repositório de usuários (injetado automaticamente)

    Returns:
        UserResponse com dados do usuário

    Raises:
        HTTPException 404: Se o usuário não for encontrado

    Exemplo de resposta:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "João Silva",
            "email": "joao@example.com",
            "role": "author",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    """
    user = await repo.get(user_id)

    # Retorna 404 se não encontrado
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    return UserResponse.model_validate(user)


# =============================================================================
# Endpoints de Escrita (POST, PATCH, DELETE)
# =============================================================================


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, repo: UserRepo):
    """
    Cria um novo usuário no sistema.

    A senha é automaticamente hasheada com bcrypt antes de ser armazenada.
    Emails devem ser únicos no sistema.

    Args:
        data: Dados do usuário a ser criado (UserCreate schema)
        repo: Repositório de usuários (injetado automaticamente)

    Returns:
        UserResponse com dados do usuário criado (sem a senha)

    Raises:
        HTTPException 400: Se o email já estiver cadastrado

    Body (JSON):
        {
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "senha_segura_123",
            "role": "author"  // opcional, default: "author"
        }

    Segurança:
        - Senha mínima de 8 caracteres (validado pelo schema)
        - Senha hasheada com bcrypt (custo padrão)
        - Email validado como único para evitar duplicação
    """
    # Valida unicidade do email antes de criar
    if await repo.email_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado",
        )

    # Converte schema para dict e processa a senha
    user_data = data.model_dump()

    # Remove senha plain text e adiciona hash
    # bcrypt gera salt automaticamente e inclui no hash
    user_data["password_hash"] = bcrypt.hash(user_data.pop("password"))

    # Persiste e retorna usuário criado
    user = await repo.create(user_data)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, data: UserUpdate, repo: UserRepo):
    """
    Atualiza um usuário existente (atualização parcial).

    Permite atualizar apenas os campos enviados no body.
    Se o email for alterado, verifica se o novo email não está em uso.

    Args:
        user_id: UUID do usuário a ser atualizado
        data: Campos a serem atualizados (UserUpdate schema)
        repo: Repositório de usuários (injetado automaticamente)

    Returns:
        UserResponse com dados atualizados do usuário

    Raises:
        HTTPException 404: Se o usuário não for encontrado
        HTTPException 400: Se o novo email já estiver em uso

    Body (JSON) - todos os campos são opcionais:
        {
            "name": "Novo Nome",
            "email": "novo@email.com",
            "role": "editor",
            "is_active": false
        }

    Notas:
        - Campos não enviados mantêm seus valores atuais
        - Para alterar senha, usar endpoint específico (a implementar)
    """
    # Busca usuário existente
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    # Se está alterando email, verifica se o novo email já existe
    if data.email and data.email != user.email:
        if await repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ja cadastrado",
            )

    # Extrai apenas campos que foram enviados (exclude_unset=True)
    update_data = data.model_dump(exclude_unset=True)

    # Atualiza e retorna
    user = await repo.update(user, update_data)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def delete_user(user_id: UUID, repo: UserRepo):
    """
    Remove um usuário do sistema.

    Realiza hard delete (remoção física do banco).
    Para soft delete, considere usar update com is_active=false.

    Args:
        user_id: UUID do usuário a ser removido
        repo: Repositório de usuários (injetado automaticamente)

    Returns:
        MessageResponse confirmando a remoção

    Raises:
        HTTPException 401: Se não estiver autenticado
        HTTPException 403: Se não for admin
        HTTPException 404: Se o usuário não for encontrado

    Exemplo de resposta:
        {
            "message": "Usuario removido com sucesso",
            "success": true
        }

    Cuidados:
        - Esta ação é irreversível
        - Posts do usuário terão author_id definido como NULL
        - Apenas administradores podem executar esta ação
    """
    # Verifica existência antes de deletar (mais eficiente que get completo)
    if not await repo.exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    # Remove usuário
    await repo.delete(user_id)

    return MessageResponse(message="Usuario removido com sucesso")
