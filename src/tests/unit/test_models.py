"""
Testes unitarios para SQLAlchemy models.

Nota: Os defaults (server_default) so sao aplicados pelo banco de dados.
Ao criar instancias em memoria, precisamos passar os valores explicitamente.
"""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.models import (
    Category,
    NewsletterSignup,
    Post,
    Product,
    User,
)
from app.models.post import PostStatus, PostType
from app.models.product import PriceRange, ProductAvailability, ProductPlatform
from app.models.user import UserRole


# =============================================================================
# User Model
# =============================================================================


class TestUserModel:
    """Testes para model User."""

    def test_user_creation(self):
        """Deve criar usuario com atributos corretos."""
        user = User(
            name="Test User",
            email="test@example.com",
            password_hash="hashed_password",
            role=UserRole.AUTHOR,
            is_active=True,
        )
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == UserRole.AUTHOR
        assert user.is_active is True

    def test_user_roles(self):
        """Deve suportar todos os roles."""
        for role in UserRole:
            user = User(
                name="User",
                email=f"{role.value}@test.com",
                password_hash="hash",
                role=role,
            )
            assert user.role == role

    def test_user_repr(self):
        """Deve ter representacao string legivel."""
        user = User(
            id=uuid4(),
            name="Test",
            email="test@example.com",
            password_hash="hash",
            role=UserRole.ADMIN,
        )
        repr_str = repr(user)
        assert "User" in repr_str
        assert "test@example.com" in repr_str


# =============================================================================
# Category Model
# =============================================================================


class TestCategoryModel:
    """Testes para model Category."""

    def test_category_creation(self):
        """Deve criar categoria com atributos corretos."""
        category = Category(
            name="Funko Pop",
            slug="funko-pop",
            description="Bonecos colecionaveis",
        )
        assert category.name == "Funko Pop"
        assert category.slug == "funko-pop"

    def test_category_hierarchy(self):
        """Deve suportar hierarquia de categorias."""
        parent = Category(
            id=uuid4(),
            name="Colecionaveis",
            slug="colecionaveis",
        )
        child = Category(
            name="Funko Pop",
            slug="funko-pop",
            parent_id=parent.id,
        )
        assert child.parent_id == parent.id

    def test_category_repr(self):
        """Deve ter representacao string legivel."""
        category = Category(
            id=uuid4(),
            name="Test Category",
            slug="test-category",
        )
        repr_str = repr(category)
        assert "Category" in repr_str
        assert "test-category" in repr_str


# =============================================================================
# Post Model
# =============================================================================


class TestPostModel:
    """Testes para model Post."""

    def test_post_creation(self):
        """Deve criar post com atributos corretos."""
        post = Post(
            type=PostType.LISTICLE,
            title="Top 10 Produtos",
            slug="top-10-produtos",
            content="<p>Conteudo aqui</p>",
            status=PostStatus.DRAFT,
        )
        assert post.title == "Top 10 Produtos"
        assert post.type == PostType.LISTICLE
        assert post.status == PostStatus.DRAFT

    def test_post_types(self):
        """Deve suportar todos os tipos de post."""
        for post_type in PostType:
            post = Post(
                type=post_type,
                title="Test",
                slug=f"test-{post_type.value}",
                content="content",
            )
            assert post.type == post_type

    def test_post_statuses(self):
        """Deve suportar todos os status."""
        for status in PostStatus:
            post = Post(
                type=PostType.GUIDE,
                title="Test",
                slug=f"test-{status.value}",
                content="content",
                status=status,
            )
            assert post.status == status

    def test_post_with_counters(self):
        """Deve aceitar contadores explicitamente."""
        post = Post(
            type=PostType.PRODUCT_SINGLE,
            title="Test",
            slug="test",
            content="content",
            status=PostStatus.PUBLISHED,
            view_count=100,
            click_count=50,
        )
        assert post.view_count == 100
        assert post.click_count == 50

    def test_post_tags_as_list(self):
        """Deve aceitar tags como lista."""
        post = Post(
            type=PostType.LISTICLE,
            title="Test",
            slug="test",
            content="content",
            tags=["geek", "presentes"],
        )
        assert post.tags == ["geek", "presentes"]

    def test_post_repr(self):
        """Deve ter representacao string legivel."""
        post = Post(
            id=uuid4(),
            type=PostType.GUIDE,
            title="Test Post",
            slug="test-post",
            content="content",
            status=PostStatus.DRAFT,
        )
        repr_str = repr(post)
        assert "Post" in repr_str
        assert "test-post" in repr_str


# =============================================================================
# Product Model
# =============================================================================


class TestProductModel:
    """Testes para model Product."""

    def test_product_creation(self):
        """Deve criar produto com atributos corretos."""
        product = Product(
            name="Funko Pop Vader",
            slug="funko-pop-vader",
            price=Decimal("149.90"),
            affiliate_url_raw="https://amazon.com.br/dp/123",
            affiliate_redirect_slug="funko-vader",
            platform=ProductPlatform.AMAZON,
        )
        assert product.name == "Funko Pop Vader"
        assert product.price == Decimal("149.90")
        assert product.platform == ProductPlatform.AMAZON

    def test_product_platforms(self):
        """Deve suportar todas as plataformas."""
        for platform in ProductPlatform:
            product = Product(
                name="Test",
                slug=f"test-{platform.value}",
                affiliate_url_raw="https://test.com",
                affiliate_redirect_slug=f"test-{platform.value}",
                platform=platform,
            )
            assert product.platform == platform

    def test_product_availability(self):
        """Deve suportar todos os status de disponibilidade."""
        for availability in ProductAvailability:
            product = Product(
                name="Test",
                slug=f"test-{availability.value}",
                affiliate_url_raw="https://test.com",
                affiliate_redirect_slug=f"test-{availability.value}",
                platform=ProductPlatform.AMAZON,
                availability=availability,
            )
            assert product.availability == availability

    def test_product_price_ranges(self):
        """Deve suportar todas as faixas de preco."""
        for price_range in PriceRange:
            product = Product(
                name="Test",
                slug=f"test-{price_range.value}",
                affiliate_url_raw="https://test.com",
                affiliate_redirect_slug=f"test-{price_range.value.replace('+', 'plus')}",
                platform=ProductPlatform.AMAZON,
                price_range=price_range,
            )
            assert product.price_range == price_range

    def test_product_with_counters(self):
        """Deve aceitar contadores explicitamente."""
        product = Product(
            name="Test",
            slug="test",
            affiliate_url_raw="https://test.com",
            affiliate_redirect_slug="test",
            platform=ProductPlatform.AMAZON,
            click_count=100,
            review_count=50,
        )
        assert product.click_count == 100
        assert product.review_count == 50

    def test_product_repr(self):
        """Deve ter representacao string legivel."""
        product = Product(
            id=uuid4(),
            name="Test Product",
            slug="test-product",
            affiliate_url_raw="https://test.com",
            affiliate_redirect_slug="test",
            platform=ProductPlatform.MERCADOLIVRE,
        )
        repr_str = repr(product)
        assert "Product" in repr_str
        assert "Test Product" in repr_str


# =============================================================================
# Newsletter Model
# =============================================================================


class TestNewsletterModel:
    """Testes para model NewsletterSignup."""

    def test_newsletter_creation(self):
        """Deve criar inscricao com atributos corretos."""
        signup = NewsletterSignup(
            email="test@example.com",
            name="Test User",
            source="homepage",
            is_active=True,
        )
        assert signup.email == "test@example.com"
        assert signup.name == "Test User"
        assert signup.is_active is True

    def test_newsletter_minimal(self):
        """Deve criar inscricao apenas com email."""
        signup = NewsletterSignup(email="minimal@test.com")
        assert signup.email == "minimal@test.com"
        assert signup.name is None
        assert signup.source is None

    def test_newsletter_repr(self):
        """Deve ter representacao string legivel."""
        signup = NewsletterSignup(
            id=uuid4(),
            email="test@example.com",
            is_active=True,
        )
        repr_str = repr(signup)
        assert "NewsletterSignup" in repr_str
        assert "test@example.com" in repr_str
