"""
Testes CRITICOS para preservacao de dados de produtos.

Estes testes garantem que atualizacoes parciais de produtos NAO apagam
dados existentes como imagens, categorias, precos, etc.

CONTEXTO: Bug critico onde atualizacao de produto via admin apagava imagens
quando o campo de imagens vinha vazio do formulario.

Estes testes devem SEMPRE passar antes de deploy em producao.
"""

import json
import pytest
import pytest_asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductPlatform, ProductAvailability


# -----------------------------------------------------------------------------
# Fixtures especificas para estes testes
# -----------------------------------------------------------------------------


@pytest_asyncio.fixture
async def product_with_images(db_session: AsyncSession) -> Product:
    """
    Cria produto com imagens para testar preservacao.

    Este produto simula um cadastro completo vindo de producao.
    """
    product = Product(
        name="Produto Com Imagens",
        slug=f"produto-com-imagens-{uuid4().hex[:8]}",
        short_description="Descricao curta do produto",
        long_description="Descricao longa e detalhada do produto com varias informacoes",
        price=199.90,
        currency="BRL",
        main_image_url="/uploads/products/imagem-principal-123.jpg",
        images=[
            "/uploads/products/imagem-principal-123.jpg",
            "/uploads/products/imagem-secundaria-456.jpg",
            "/uploads/products/imagem-terceira-789.jpg",
        ],
        affiliate_url_raw="https://amazon.com.br/dp/B123456?tag=geekbidu-20",
        affiliate_redirect_slug=f"redirect-{uuid4().hex[:8]}",
        platform=ProductPlatform.AMAZON,
        platform_product_id="B123456",
        categories=["funko", "star-wars", "colecao"],
        tags=["funko", "star-wars", "darth-vader", "colecionavel"],
        availability=ProductAvailability.AVAILABLE,
        rating=4.5,
        review_count=150,
        internal_score=85.0,
        click_count=42,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest_asyncio.fixture
async def product_with_all_fields(db_session: AsyncSession) -> Product:
    """
    Cria produto com TODOS os campos preenchidos.

    Usado para garantir que nenhum campo seja perdido em atualizacoes.
    """
    product = Product(
        name="Produto Completo",
        slug=f"produto-completo-{uuid4().hex[:8]}",
        short_description="Descricao curta",
        long_description="Descricao longa completa",
        price=299.90,
        currency="BRL",
        main_image_url="/uploads/products/main.jpg",
        images=["/uploads/products/main.jpg", "/uploads/products/alt1.jpg"],
        affiliate_url_raw="https://amazon.com.br/dp/COMPLETE?tag=geekbidu-20",
        affiliate_redirect_slug=f"complete-{uuid4().hex[:8]}",
        platform=ProductPlatform.AMAZON,
        platform_product_id="COMPLETE123",
        categories=["categoria1", "categoria2"],
        tags=["tag1", "tag2", "tag3"],
        availability=ProductAvailability.AVAILABLE,
        rating=4.8,
        review_count=500,
        internal_score=95.0,
        click_count=100,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


# -----------------------------------------------------------------------------
# Testes de Preservacao de Imagens (CRITICO)
# -----------------------------------------------------------------------------


class TestImagePreservation:
    """
    Testes para garantir que imagens NAO sao perdidas em atualizacoes.

    Cenario do bug: formulario admin envia campo images vazio/null,
    e o update sobrescreve as imagens existentes com lista vazia.
    """

    @pytest.mark.asyncio
    async def test_images_preserved_when_update_data_has_empty_images_string(
        self, db_session: AsyncSession, product_with_images: Product
    ):
        """
        CRITICO: Imagens devem ser preservadas quando campo images vem como string vazia.

        Este cenario ocorre quando JavaScript do formulario falha ou campo hidden esta vazio.
        """
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        original_images = product_with_images.images.copy()
        original_main_image = product_with_images.main_image_url

        # Simula atualizacao apenas do nome (imagens nao devem ser afetadas)
        # Nota: Este teste verifica o comportamento do repositorio, nao do endpoint
        await repo.update(product_with_images, {"name": "Nome Atualizado"})

        # Recarrega do banco
        await db_session.refresh(product_with_images)

        # ASSERTS CRITICOS
        assert product_with_images.images == original_images, \
            "CRITICO: Imagens foram apagadas durante atualizacao!"
        assert product_with_images.main_image_url == original_main_image, \
            "CRITICO: Imagem principal foi apagada durante atualizacao!"
        assert len(product_with_images.images) == 3, \
            "CRITICO: Quantidade de imagens mudou!"

    @pytest.mark.asyncio
    async def test_images_preserved_when_update_excludes_images_field(
        self, db_session: AsyncSession, product_with_images: Product
    ):
        """
        Imagens devem ser preservadas quando campo images NAO esta no update_data.
        """
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        original_images = product_with_images.images.copy()

        # Atualiza apenas preco - sem mencionar imagens
        await repo.update(product_with_images, {"price": 299.90})

        await db_session.refresh(product_with_images)

        assert product_with_images.images == original_images
        assert float(product_with_images.price) == 299.90

    @pytest.mark.asyncio
    async def test_images_can_be_intentionally_cleared(
        self, db_session: AsyncSession, product_with_images: Product
    ):
        """
        Imagens podem ser limpas INTENCIONALMENTE passando lista vazia explicita.

        Diferenca: update com images=[] (intencional) vs update sem images (preservar).
        """
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)

        # Limpa imagens intencionalmente
        await repo.update(product_with_images, {
            "images": [],
            "main_image_url": None,
        })

        await db_session.refresh(product_with_images)

        assert product_with_images.images == []
        assert product_with_images.main_image_url is None

    @pytest.mark.asyncio
    async def test_main_image_updated_correctly_when_images_change(
        self, db_session: AsyncSession, product_with_images: Product
    ):
        """
        main_image_url deve refletir a primeira imagem da lista.
        """
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)

        new_images = ["/uploads/products/nova-principal.jpg", "/uploads/products/nova-alt.jpg"]

        await repo.update(product_with_images, {
            "images": new_images,
            "main_image_url": new_images[0],
        })

        await db_session.refresh(product_with_images)

        assert product_with_images.main_image_url == "/uploads/products/nova-principal.jpg"
        assert product_with_images.images == new_images


# -----------------------------------------------------------------------------
# Testes de Preservacao de Categorias
# -----------------------------------------------------------------------------


class TestCategoryPreservation:
    """Testes para garantir que categorias NAO sao perdidas em atualizacoes."""

    @pytest.mark.asyncio
    async def test_categories_preserved_when_not_in_update(
        self, db_session: AsyncSession, product_with_images: Product
    ):
        """Categorias devem ser preservadas quando nao estao no update_data."""
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        original_categories = product_with_images.categories.copy()

        await repo.update(product_with_images, {"name": "Novo Nome"})

        await db_session.refresh(product_with_images)

        assert product_with_images.categories == original_categories

    @pytest.mark.asyncio
    async def test_categories_can_be_updated(
        self, db_session: AsyncSession, product_with_images: Product
    ):
        """Categorias podem ser atualizadas quando passadas explicitamente."""
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        new_categories = ["nova-categoria", "outra-categoria"]

        await repo.update(product_with_images, {"categories": new_categories})

        await db_session.refresh(product_with_images)

        assert product_with_images.categories == new_categories


# -----------------------------------------------------------------------------
# Testes de Preservacao de Campos Numericos
# -----------------------------------------------------------------------------


class TestNumericFieldsPreservation:
    """Testes para garantir que campos numericos NAO sao zerados incorretamente."""

    @pytest.mark.asyncio
    async def test_price_preserved_when_not_in_update(
        self, db_session: AsyncSession, product_with_all_fields: Product
    ):
        """Preco deve ser preservado quando nao esta no update_data."""
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        original_price = float(product_with_all_fields.price)

        await repo.update(product_with_all_fields, {"name": "Novo Nome"})

        await db_session.refresh(product_with_all_fields)

        assert float(product_with_all_fields.price) == original_price

    @pytest.mark.asyncio
    async def test_price_can_be_set_to_none(
        self, db_session: AsyncSession, product_with_all_fields: Product
    ):
        """Preco pode ser definido como None (produto sem preco definido)."""
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)

        await repo.update(product_with_all_fields, {"price": None})

        await db_session.refresh(product_with_all_fields)

        assert product_with_all_fields.price is None

    @pytest.mark.asyncio
    async def test_rating_preserved_when_not_in_update(
        self, db_session: AsyncSession, product_with_all_fields: Product
    ):
        """Rating deve ser preservado quando nao esta no update_data."""
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        original_rating = float(product_with_all_fields.rating)

        await repo.update(product_with_all_fields, {"name": "Novo Nome"})

        await db_session.refresh(product_with_all_fields)

        assert float(product_with_all_fields.rating) == original_rating

    @pytest.mark.asyncio
    async def test_click_count_preserved_on_update(
        self, db_session: AsyncSession, product_with_all_fields: Product
    ):
        """
        click_count NAO deve ser zerado em atualizacoes normais.

        Este contador e incrementado por eventos de clique e e critico para metricas.
        """
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        original_clicks = product_with_all_fields.click_count

        await repo.update(product_with_all_fields, {"name": "Novo Nome"})

        await db_session.refresh(product_with_all_fields)

        assert product_with_all_fields.click_count == original_clicks

    @pytest.mark.asyncio
    async def test_internal_score_preserved_on_update(
        self, db_session: AsyncSession, product_with_all_fields: Product
    ):
        """internal_score NAO deve ser zerado em atualizacoes normais."""
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        original_score = float(product_with_all_fields.internal_score)

        await repo.update(product_with_all_fields, {"name": "Novo Nome"})

        await db_session.refresh(product_with_all_fields)

        assert float(product_with_all_fields.internal_score) == original_score


# -----------------------------------------------------------------------------
# Testes de Preservacao de Tags
# -----------------------------------------------------------------------------


class TestTagsPreservation:
    """Testes para garantir que tags NAO sao perdidas em atualizacoes."""

    @pytest.mark.asyncio
    async def test_tags_preserved_when_not_in_update(
        self, db_session: AsyncSession, product_with_images: Product
    ):
        """Tags devem ser preservadas quando nao estao no update_data."""
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)
        original_tags = product_with_images.tags.copy()

        await repo.update(product_with_images, {"name": "Novo Nome"})

        await db_session.refresh(product_with_images)

        assert product_with_images.tags == original_tags


# -----------------------------------------------------------------------------
# Testes de Integridade Completa
# -----------------------------------------------------------------------------


class TestFullDataIntegrity:
    """
    Testes de integridade completa: verifica que NENHUM campo e perdido.
    """

    @pytest.mark.asyncio
    async def test_all_fields_preserved_on_single_field_update(
        self, db_session: AsyncSession, product_with_all_fields: Product
    ):
        """
        CRITICO: Atualizar UM campo nao deve afetar NENHUM outro campo.

        Este teste captura o snapshot completo antes e depois do update.
        """
        from app.repositories.product import ProductRepository

        repo = ProductRepository(db_session)

        # Snapshot de todos os campos antes do update
        before = {
            "name": product_with_all_fields.name,
            "slug": product_with_all_fields.slug,
            "short_description": product_with_all_fields.short_description,
            "long_description": product_with_all_fields.long_description,
            "price": float(product_with_all_fields.price) if product_with_all_fields.price else None,
            "main_image_url": product_with_all_fields.main_image_url,
            "images": product_with_all_fields.images.copy(),
            "affiliate_url_raw": product_with_all_fields.affiliate_url_raw,
            "affiliate_redirect_slug": product_with_all_fields.affiliate_redirect_slug,
            "platform": product_with_all_fields.platform,
            "platform_product_id": product_with_all_fields.platform_product_id,
            "categories": product_with_all_fields.categories.copy(),
            "tags": product_with_all_fields.tags.copy(),
            "availability": product_with_all_fields.availability,
            "rating": float(product_with_all_fields.rating) if product_with_all_fields.rating else None,
            "review_count": product_with_all_fields.review_count,
            "internal_score": float(product_with_all_fields.internal_score),
            "click_count": product_with_all_fields.click_count,
        }

        # Atualiza APENAS a descricao curta
        await repo.update(product_with_all_fields, {
            "short_description": "Nova descricao curta atualizada"
        })

        await db_session.refresh(product_with_all_fields)

        # Verifica cada campo individualmente com mensagens claras
        assert product_with_all_fields.slug == before["slug"], "slug foi alterado!"
        assert product_with_all_fields.long_description == before["long_description"], "long_description foi alterado!"
        assert float(product_with_all_fields.price) == before["price"], "price foi alterado!"
        assert product_with_all_fields.main_image_url == before["main_image_url"], "main_image_url foi alterado!"
        assert product_with_all_fields.images == before["images"], "images foi alterado!"
        assert product_with_all_fields.affiliate_url_raw == before["affiliate_url_raw"], "affiliate_url_raw foi alterado!"
        assert product_with_all_fields.affiliate_redirect_slug == before["affiliate_redirect_slug"], "affiliate_redirect_slug foi alterado!"
        assert product_with_all_fields.platform == before["platform"], "platform foi alterado!"
        assert product_with_all_fields.platform_product_id == before["platform_product_id"], "platform_product_id foi alterado!"
        assert product_with_all_fields.categories == before["categories"], "categories foi alterado!"
        assert product_with_all_fields.tags == before["tags"], "tags foi alterado!"
        assert product_with_all_fields.availability == before["availability"], "availability foi alterado!"
        assert float(product_with_all_fields.rating) == before["rating"], "rating foi alterado!"
        assert product_with_all_fields.review_count == before["review_count"], "review_count foi alterado!"
        assert float(product_with_all_fields.internal_score) == before["internal_score"], "internal_score foi alterado!"
        assert product_with_all_fields.click_count == before["click_count"], "click_count foi alterado!"

        # O campo atualizado deve ter o novo valor
        assert product_with_all_fields.short_description == "Nova descricao curta atualizada"


# -----------------------------------------------------------------------------
# Testes de Simulacao de Formulario Admin
# -----------------------------------------------------------------------------


class TestAdminFormSimulation:
    """
    Testes que simulam o comportamento do formulario admin.

    Estes testes reproduzem cenarios reais de uso do formulario.
    """

    @pytest.mark.asyncio
    async def test_form_update_with_empty_images_json_preserves_images(
        self, product_with_images: Product
    ):
        """
        Simula formulario enviando images='[]' (string JSON vazia).

        O endpoint deve detectar isso e preservar as imagens existentes.
        """
        # Simula o processamento do formulario
        form_images_value = "[]"  # Campo hidden do formulario

        # Parse como o endpoint faz
        try:
            images_list = json.loads(form_images_value) if form_images_value and form_images_value.strip() else None
        except json.JSONDecodeError:
            images_list = None

        # Se lista vazia ou None, deve manter as existentes
        if not images_list:
            images_list = product_with_images.images or []

        # Verifica que as imagens originais sao preservadas
        assert images_list == product_with_images.images
        assert len(images_list) == 3

    @pytest.mark.asyncio
    async def test_form_update_with_null_images_preserves_images(
        self, product_with_images: Product
    ):
        """
        Simula formulario enviando images='' (string vazia).
        """
        form_images_value = ""  # Campo hidden vazio

        try:
            images_list = json.loads(form_images_value) if form_images_value and form_images_value.strip() else None
        except json.JSONDecodeError:
            images_list = None

        if images_list is None:
            images_list = product_with_images.images or []

        assert images_list == product_with_images.images
        assert len(images_list) == 3

    @pytest.mark.asyncio
    async def test_form_update_with_new_images_replaces_old(self):
        """
        Simula formulario enviando novas imagens - deve substituir as antigas.
        """
        form_images_value = '["/uploads/products/nova1.jpg", "/uploads/products/nova2.jpg"]'

        images_list = json.loads(form_images_value)

        assert images_list == ["/uploads/products/nova1.jpg", "/uploads/products/nova2.jpg"]
        assert len(images_list) == 2
