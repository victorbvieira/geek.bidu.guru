"""
Testes para o painel administrativo.

Verifica:
- Autenticacao do admin
- Acesso as rotas protegidas
- CRUD de posts, produtos, categorias, usuarios
"""

import pytest
from httpx import AsyncClient


class TestAdminLogin:
    """Testes para autenticacao do admin."""

    @pytest.mark.asyncio
    async def test_login_page_renders(self, client: AsyncClient):
        """Pagina de login deve ser acessivel."""
        response = await client.get("/admin/login")

        assert response.status_code == 200
        assert "Login" in response.text

    @pytest.mark.asyncio
    async def test_login_page_redirects_when_authenticated(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Pagina de login redireciona para dashboard se ja autenticado."""
        response = await client.get(
            "/admin/login",
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers.get("location") == "/admin"

    @pytest.mark.asyncio
    async def test_login_with_invalid_credentials(self, client: AsyncClient):
        """Login com credenciais invalidas retorna erro."""
        response = await client.post(
            "/admin/login",
            data={"email": "wrong@email.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "incorretos" in response.text.lower()

    @pytest.mark.asyncio
    async def test_logout_clears_cookie(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Logout remove cookie de autenticacao."""
        response = await client.get(
            "/admin/logout",
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers.get("location") == "/admin/login"


class TestAdminDashboard:
    """Testes para dashboard do admin."""

    @pytest.mark.asyncio
    async def test_dashboard_requires_auth(self, client: AsyncClient):
        """Dashboard requer autenticacao."""
        response = await client.get("/admin", follow_redirects=False)

        # Deve retornar 303 See Other para redirecionar ao login
        assert response.status_code == 303

    @pytest.mark.asyncio
    async def test_dashboard_accessible_when_authenticated(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Dashboard acessivel quando autenticado."""
        response = await client.get(
            "/admin",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Dashboard" in response.text


class TestAdminPosts:
    """Testes para CRUD de posts no admin."""

    @pytest.mark.asyncio
    async def test_posts_list_requires_auth(self, client: AsyncClient):
        """Lista de posts requer autenticacao."""
        response = await client.get("/admin/posts", follow_redirects=False)

        assert response.status_code == 303

    @pytest.mark.asyncio
    async def test_posts_list_accessible(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Lista de posts acessivel quando autenticado."""
        response = await client.get(
            "/admin/posts",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Posts" in response.text

    @pytest.mark.asyncio
    async def test_new_post_form_renders(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Formulario de novo post renderiza."""
        response = await client.get(
            "/admin/posts/new",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Novo Post" in response.text


class TestAdminProducts:
    """Testes para CRUD de produtos no admin."""

    @pytest.mark.asyncio
    async def test_products_list_accessible(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Lista de produtos acessivel quando autenticado."""
        response = await client.get(
            "/admin/products",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Produtos" in response.text

    @pytest.mark.asyncio
    async def test_new_product_form_renders(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Formulario de novo produto renderiza."""
        response = await client.get(
            "/admin/products/new",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Novo Produto" in response.text


class TestAdminCategories:
    """Testes para CRUD de categorias no admin."""

    @pytest.mark.asyncio
    async def test_categories_list_accessible(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Lista de categorias acessivel quando autenticado."""
        response = await client.get(
            "/admin/categories",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Categorias" in response.text

    @pytest.mark.asyncio
    async def test_new_category_form_renders(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Formulario de nova categoria renderiza."""
        response = await client.get(
            "/admin/categories/new",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Nova Categoria" in response.text


class TestAdminUsers:
    """Testes para CRUD de usuarios no admin (apenas admin)."""

    @pytest.mark.asyncio
    async def test_users_list_requires_admin_role(
        self, client: AsyncClient, editor_auth_cookie: dict
    ):
        """Lista de usuarios requer role admin."""
        response = await client.get(
            "/admin/users",
            cookies=editor_auth_cookie,
        )

        # Editor nao pode acessar usuarios
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_users_list_accessible_by_admin(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Lista de usuarios acessivel por admin."""
        response = await client.get(
            "/admin/users",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Usuarios" in response.text

    @pytest.mark.asyncio
    async def test_new_user_form_renders(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Formulario de novo usuario renderiza."""
        response = await client.get(
            "/admin/users/new",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 200
        assert "Novo Usuario" in response.text
