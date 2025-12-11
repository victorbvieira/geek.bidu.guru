"""
Testes unitarios para Pydantic schemas.
"""

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    NewsletterCreate,
    NewsletterSubscribe,
    PaginatedResponse,
    PaginationParams,
    PostCreate,
    ProductCreate,
    UserCreate,
    UserLogin,
    UserUpdate,
)


# =============================================================================
# User Schemas
# =============================================================================


class TestUserSchemas:
    """Testes para schemas de User."""

    def test_user_create_valid(self, user_data):
        """Deve criar usuario com dados validos."""
        schema = UserCreate(**user_data)
        assert schema.name == user_data["name"]
        assert schema.email == user_data["email"]
        assert schema.password == user_data["password"]

    def test_user_create_invalid_email(self, user_data):
        """Deve rejeitar email invalido."""
        user_data["email"] = "invalid-email"
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "email" in str(exc_info.value)

    def test_user_create_password_too_short(self, user_data):
        """Deve rejeitar senha muito curta."""
        user_data["password"] = "short"
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "password" in str(exc_info.value)

    def test_user_create_name_too_short(self, user_data):
        """Deve rejeitar nome muito curto."""
        user_data["name"] = "A"
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "name" in str(exc_info.value)

    def test_user_update_partial(self):
        """Deve permitir atualizacao parcial."""
        schema = UserUpdate(name="New Name")
        assert schema.name == "New Name"
        assert schema.email is None
        assert schema.role is None

    def test_user_login_valid(self):
        """Deve validar login com dados corretos."""
        schema = UserLogin(email="user@example.com", password="password123")
        assert schema.email == "user@example.com"


# =============================================================================
# Category Schemas
# =============================================================================


class TestCategorySchemas:
    """Testes para schemas de Category."""

    def test_category_create_valid(self, category_data):
        """Deve criar categoria com dados validos."""
        schema = CategoryCreate(**category_data)
        assert schema.name == category_data["name"]
        assert schema.slug == category_data["slug"]

    def test_category_create_with_parent(self, category_data):
        """Deve criar categoria com parent_id."""
        category_data["parent_id"] = uuid4()
        schema = CategoryCreate(**category_data)
        assert schema.parent_id is not None

    def test_category_create_name_too_short(self, category_data):
        """Deve rejeitar nome muito curto."""
        category_data["name"] = "A"
        with pytest.raises(ValidationError):
            CategoryCreate(**category_data)

    def test_category_response_from_attributes(self, category_data):
        """Deve criar response a partir de atributos."""
        from datetime import datetime

        data = {
            **category_data,
            "id": uuid4(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        schema = CategoryResponse(**data)
        assert schema.id == data["id"]


# =============================================================================
# Post Schemas
# =============================================================================


class TestPostSchemas:
    """Testes para schemas de Post."""

    def test_post_create_valid(self, post_data):
        """Deve criar post com dados validos."""
        schema = PostCreate(**post_data)
        assert schema.title == post_data["title"]
        assert schema.slug == post_data["slug"]
        assert schema.type.value == post_data["type"]

    def test_post_create_seo_title_too_long(self, post_data):
        """Deve rejeitar SEO title maior que 60 chars."""
        post_data["seo_title"] = "A" * 61
        with pytest.raises(ValidationError) as exc_info:
            PostCreate(**post_data)
        assert "seo_title" in str(exc_info.value)

    def test_post_create_seo_description_too_long(self, post_data):
        """Deve rejeitar SEO description maior que 160 chars."""
        post_data["seo_description"] = "A" * 161
        with pytest.raises(ValidationError) as exc_info:
            PostCreate(**post_data)
        assert "seo_description" in str(exc_info.value)

    def test_post_create_with_category(self, post_data):
        """Deve criar post com category_id."""
        post_data["category_id"] = uuid4()
        schema = PostCreate(**post_data)
        assert schema.category_id is not None

    def test_post_create_default_status(self, post_data):
        """Deve usar status draft por padrao."""
        del post_data["status"]
        schema = PostCreate(**post_data)
        assert schema.status.value == "draft"


# =============================================================================
# Product Schemas
# =============================================================================


class TestProductSchemas:
    """Testes para schemas de Product."""

    def test_product_create_valid(self, product_data):
        """Deve criar produto com dados validos."""
        schema = ProductCreate(**product_data)
        assert schema.name == product_data["name"]
        assert schema.platform.value == product_data["platform"]
        assert schema.price == Decimal(product_data["price"])

    def test_product_create_invalid_redirect_slug(self, product_data):
        """Deve rejeitar redirect_slug com caracteres invalidos."""
        product_data["affiliate_redirect_slug"] = "Invalid Slug!"
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "affiliate_redirect_slug" in str(exc_info.value)

    def test_product_create_valid_redirect_slug(self, product_data):
        """Deve aceitar redirect_slug valido."""
        product_data["affiliate_redirect_slug"] = "valid-slug-123"
        schema = ProductCreate(**product_data)
        assert schema.affiliate_redirect_slug == "valid-slug-123"

    def test_product_create_rating_range(self, product_data):
        """Deve validar rating entre 0 e 5."""
        product_data["rating"] = "5.5"
        with pytest.raises(ValidationError):
            ProductCreate(**product_data)

        product_data["rating"] = "-0.5"
        with pytest.raises(ValidationError):
            ProductCreate(**product_data)


# =============================================================================
# Newsletter Schemas
# =============================================================================


class TestNewsletterSchemas:
    """Testes para schemas de Newsletter."""

    def test_newsletter_create_valid(self, newsletter_data):
        """Deve criar inscricao com dados validos."""
        schema = NewsletterCreate(**newsletter_data)
        assert schema.email == newsletter_data["email"]
        assert schema.name == newsletter_data["name"]

    def test_newsletter_subscribe_minimal(self):
        """Deve criar inscricao apenas com email."""
        schema = NewsletterSubscribe(email="test@example.com")
        assert schema.email == "test@example.com"
        assert schema.name is None

    def test_newsletter_invalid_email(self):
        """Deve rejeitar email invalido."""
        with pytest.raises(ValidationError):
            NewsletterSubscribe(email="not-an-email")


# =============================================================================
# Pagination Schemas
# =============================================================================


class TestPaginationSchemas:
    """Testes para schemas de paginacao."""

    def test_pagination_params_defaults(self):
        """Deve usar valores padrao."""
        params = PaginationParams()
        assert params.page == 1
        assert params.per_page == 20
        assert params.offset == 0

    def test_pagination_params_offset_calculation(self):
        """Deve calcular offset corretamente."""
        params = PaginationParams(page=3, per_page=10)
        assert params.offset == 20

    def test_pagination_params_validation(self):
        """Deve validar limites."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)  # page deve ser >= 1

        with pytest.raises(ValidationError):
            PaginationParams(per_page=101)  # per_page deve ser <= 100

    def test_paginated_response_create(self):
        """Deve criar resposta paginada."""
        items = [{"id": 1}, {"id": 2}]
        response = PaginatedResponse.create(
            items=items,
            total=50,
            page=1,
            per_page=20,
        )
        assert response.items == items
        assert response.total == 50
        assert response.pages == 3
