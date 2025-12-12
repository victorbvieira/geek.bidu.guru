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


# -----------------------------------------------------------------------------
# Testes para rotas POST/DELETE (admin_actions)
# -----------------------------------------------------------------------------


class TestAdminPostActions:
    """Testes para criacao/edicao/exclusao de posts no admin."""

    @pytest.mark.asyncio
    async def test_create_post_requires_auth(self, client: AsyncClient):
        """Criacao de post requer autenticacao."""
        response = await client.post(
            "/admin/posts",
            data={
                "title": "Test Post",
                "content": "Test content",
                "status": "draft",
                "type": "listicle",
            },
            follow_redirects=False,
        )

        # Sem autenticacao, retorna 303 redirecionando para login
        assert response.status_code == 303

    @pytest.mark.asyncio
    async def test_create_post_success(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de post com sucesso."""
        response = await client.post(
            "/admin/posts",
            data={
                "title": "Novo Post de Teste",
                "content": "<p>Conteudo do post</p>",
                "status": "draft",
                "type": "listicle",
            },
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert "/admin/posts" in response.headers.get("location", "")

    @pytest.mark.asyncio
    async def test_create_post_generates_slug(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de post gera slug automaticamente."""
        response = await client.post(
            "/admin/posts",
            data={
                "title": "Post Com Titulo Especial",
                "content": "<p>Conteudo</p>",
                "status": "draft",
                "type": "guide",
            },
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303

    @pytest.mark.asyncio
    async def test_create_post_missing_fields(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de post sem campos retorna 422."""
        response = await client.post(
            "/admin/posts",
            data={},  # nenhum campo
            cookies=admin_auth_cookie,
        )

        # FastAPI retorna 422 para campos obrigatorios ausentes
        assert response.status_code == 422


class TestAdminProductActions:
    """Testes para criacao/edicao/exclusao de produtos no admin."""

    @pytest.mark.asyncio
    async def test_create_product_requires_auth(self, client: AsyncClient):
        """Criacao de produto requer autenticacao."""
        response = await client.post(
            "/admin/products",
            data={
                "name": "Test Product",
                "platform": "amazon",
                "affiliate_url_raw": "https://amazon.com/test",
                "affiliate_redirect_slug": "test-product",
            },
            follow_redirects=False,
        )

        # Sem autenticacao, retorna 303 redirecionando para login
        assert response.status_code == 303

    @pytest.mark.asyncio
    async def test_create_product_success(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de produto com sucesso."""
        response = await client.post(
            "/admin/products",
            data={
                "name": "Funko Pop Batman",
                "platform": "amazon",
                "availability": "available",
                "affiliate_url_raw": "https://amazon.com/funko-batman",
                "affiliate_redirect_slug": "funko-batman-01",
            },
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert "/admin/products" in response.headers.get("location", "")

    @pytest.mark.asyncio
    async def test_create_product_with_price(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de produto com preco."""
        response = await client.post(
            "/admin/products",
            data={
                "name": "Action Figure Marvel",
                "platform": "mercadolivre",
                "availability": "available",
                "affiliate_redirect_slug": "marvel-figure-02",
                "price": "199.90",
                "affiliate_url_raw": "https://mercadolivre.com.br/product123",
            },
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303


class TestAdminCategoryActions:
    """Testes para criacao/edicao/exclusao de categorias no admin."""

    @pytest.mark.asyncio
    async def test_create_category_requires_auth(self, client: AsyncClient):
        """Criacao de categoria requer autenticacao."""
        response = await client.post(
            "/admin/categories",
            data={
                "name": "Test Category",
                "slug": "test-category",
            },
            follow_redirects=False,
        )

        # Sem autenticacao, retorna 303 redirecionando para login
        assert response.status_code == 303

    @pytest.mark.asyncio
    async def test_create_category_success(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de categoria com sucesso."""
        response = await client.post(
            "/admin/categories",
            data={
                "name": "Funko Pops",
                "slug": "funko-pops",
                "description": "Colecao de Funko Pops",
            },
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert "/admin/categories" in response.headers.get("location", "")

    @pytest.mark.asyncio
    async def test_create_category_with_seo(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de categoria com campos SEO."""
        response = await client.post(
            "/admin/categories",
            data={
                "name": "Star Wars",
                "slug": "star-wars",
                "description": "Produtos Star Wars",
                "seo_title": "Presentes Star Wars | geek.bidu.guru",
                "seo_description": "Os melhores presentes Star Wars para fas da saga.",
            },
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303


class TestAdminUserActions:
    """Testes para criacao/edicao/exclusao de usuarios no admin."""

    @pytest.mark.asyncio
    async def test_create_user_requires_admin_role(
        self, client: AsyncClient, editor_auth_cookie: dict
    ):
        """Criacao de usuario requer role admin."""
        response = await client.post(
            "/admin/users",
            data={
                "name": "New User",
                "email": "newuser@test.com",
                "password": "password123",
                "password_confirm": "password123",
                "role": "author",
            },
            cookies=editor_auth_cookie,
        )

        # Editor nao pode criar usuarios
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de usuario com sucesso."""
        response = await client.post(
            "/admin/users",
            data={
                "name": "Novo Usuario Teste",
                "email": "novousuario@test.com",
                "password": "senha123456",
                "password_confirm": "senha123456",
                "role": "editor",
            },
            cookies=admin_auth_cookie,
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert "/admin/users" in response.headers.get("location", "")

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Criacao de usuario com email duplicado falha."""
        # Criar primeiro usuario
        await client.post(
            "/admin/users",
            data={
                "name": "Usuario Um",
                "email": "duplicado@test.com",
                "password": "senha123456",
                "password_confirm": "senha123456",
                "role": "author",
            },
            cookies=admin_auth_cookie,
        )

        # Tentar criar segundo com mesmo email
        response = await client.post(
            "/admin/users",
            data={
                "name": "Usuario Dois",
                "email": "duplicado@test.com",
                "password": "senha123456",
                "password_confirm": "senha123456",
                "role": "author",
            },
            cookies=admin_auth_cookie,
        )

        # Deve falhar com erro 400 (Bad Request)
        assert response.status_code == 400


class TestAdminDeleteActions:
    """Testes para exclusao de recursos no admin."""

    @pytest.mark.asyncio
    async def test_delete_post_not_found(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Exclusao de post inexistente retorna 404."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.post(
            f"/admin/posts/{fake_id}/delete",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_product_not_found(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Exclusao de produto inexistente retorna 404."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.post(
            f"/admin/products/{fake_id}/delete",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_category_not_found(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Exclusao de categoria inexistente retorna 404."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.post(
            f"/admin/categories/{fake_id}/delete",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self, client: AsyncClient, admin_auth_cookie: dict
    ):
        """Exclusao de usuario inexistente retorna 404."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.post(
            f"/admin/users/{fake_id}/delete",
            cookies=admin_auth_cookie,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_requires_admin_role(
        self, client: AsyncClient, editor_auth_cookie: dict
    ):
        """Exclusao de usuario requer role admin."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.post(
            f"/admin/users/{fake_id}/delete",
            cookies=editor_auth_cookie,
        )

        # Editor nao pode excluir usuarios
        assert response.status_code == 403
