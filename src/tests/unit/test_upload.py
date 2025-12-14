"""
Testes unitarios para o modulo de upload de arquivos.

Verifica:
- Validacao de tipos de arquivo
- Redimensionamento de imagens
- Tamanhos padrao (categoria, produto, post)
"""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image

from app.services.upload import (
    ALLOWED_IMAGE_TYPES,
    CATEGORY_IMAGE_SIZE,
    MAX_FILE_SIZE,
    POST_FEATURED_IMAGE_SIZE,
    PRODUCT_IMAGE_SIZES,
    resize_image,
    validate_image,
)


# =============================================================================
# Testes de Configuracao
# =============================================================================


class TestUploadConstants:
    """Testes para constantes de configuracao."""

    def test_allowed_image_types(self):
        """Deve ter tipos de imagem permitidos."""
        assert "image/jpeg" in ALLOWED_IMAGE_TYPES
        assert "image/png" in ALLOWED_IMAGE_TYPES
        assert "image/webp" in ALLOWED_IMAGE_TYPES
        assert "image/gif" in ALLOWED_IMAGE_TYPES

    def test_max_file_size(self):
        """Tamanho maximo deve ser 10MB (comprimido automaticamente)."""
        assert MAX_FILE_SIZE == 10 * 1024 * 1024

    def test_category_image_size(self):
        """Tamanho de categoria deve ser 400x400."""
        assert CATEGORY_IMAGE_SIZE == (400, 400)

    def test_product_image_sizes(self):
        """Tamanhos de produto devem estar configurados."""
        assert "main" in PRODUCT_IMAGE_SIZES
        assert "thumb" in PRODUCT_IMAGE_SIZES
        assert PRODUCT_IMAGE_SIZES["main"] == (800, 800)
        assert PRODUCT_IMAGE_SIZES["thumb"] == (200, 200)

    def test_post_featured_image_size(self):
        """Tamanho de imagem de post deve ser 1200x630 (Open Graph)."""
        assert POST_FEATURED_IMAGE_SIZE == (1200, 630)


# =============================================================================
# Testes de Validacao
# =============================================================================


class TestValidateImage:
    """Testes para validacao de imagem."""

    def test_validate_jpeg(self):
        """Deve aceitar JPEG."""
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/jpeg"
        ext = validate_image(file)
        assert ext == ".jpg"

    def test_validate_png(self):
        """Deve aceitar PNG."""
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/png"
        ext = validate_image(file)
        assert ext == ".png"

    def test_validate_webp(self):
        """Deve aceitar WebP."""
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/webp"
        ext = validate_image(file)
        assert ext == ".webp"

    def test_validate_gif(self):
        """Deve aceitar GIF."""
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/gif"
        ext = validate_image(file)
        assert ext == ".gif"

    def test_reject_pdf(self):
        """Deve rejeitar PDF."""
        file = MagicMock(spec=UploadFile)
        file.content_type = "application/pdf"
        with pytest.raises(HTTPException) as exc_info:
            validate_image(file)
        assert exc_info.value.status_code == 400
        assert "Tipo de arquivo nao permitido" in exc_info.value.detail

    def test_reject_text(self):
        """Deve rejeitar texto."""
        file = MagicMock(spec=UploadFile)
        file.content_type = "text/plain"
        with pytest.raises(HTTPException):
            validate_image(file)

    def test_reject_svg(self):
        """Deve rejeitar SVG (seguranca)."""
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/svg+xml"
        with pytest.raises(HTTPException):
            validate_image(file)


# =============================================================================
# Testes de Redimensionamento
# =============================================================================


class TestResizeImage:
    """Testes para redimensionamento de imagem."""

    def create_test_image(self, width: int, height: int, mode: str = "RGB") -> bytes:
        """Cria imagem de teste."""
        img = Image.new(mode, (width, height), color="red")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        return buffer.read()

    def test_resize_square_image(self):
        """Deve redimensionar imagem quadrada."""
        content = self.create_test_image(1000, 1000)
        result = resize_image(content, (400, 400), "JPEG")

        # Verifica resultado
        img = Image.open(io.BytesIO(result))
        assert img.size == (400, 400)

    def test_resize_landscape_image(self):
        """Deve redimensionar imagem paisagem mantendo proporcao."""
        content = self.create_test_image(1200, 800)
        result = resize_image(content, (400, 400), "JPEG")

        img = Image.open(io.BytesIO(result))
        assert img.size == (400, 400)

    def test_resize_portrait_image(self):
        """Deve redimensionar imagem retrato mantendo proporcao."""
        content = self.create_test_image(800, 1200)
        result = resize_image(content, (400, 400), "JPEG")

        img = Image.open(io.BytesIO(result))
        assert img.size == (400, 400)

    def test_resize_to_category_size(self):
        """Deve redimensionar para tamanho de categoria."""
        content = self.create_test_image(1000, 800)
        result = resize_image(content, CATEGORY_IMAGE_SIZE, "JPEG")

        img = Image.open(io.BytesIO(result))
        assert img.size == CATEGORY_IMAGE_SIZE

    def test_resize_to_product_size(self):
        """Deve redimensionar para tamanho de produto."""
        content = self.create_test_image(1500, 1500)
        result = resize_image(content, PRODUCT_IMAGE_SIZES["main"], "JPEG")

        img = Image.open(io.BytesIO(result))
        assert img.size == PRODUCT_IMAGE_SIZES["main"]

    def test_resize_to_post_size(self):
        """Deve redimensionar para tamanho de post (Open Graph)."""
        content = self.create_test_image(2000, 1000)
        result = resize_image(content, POST_FEATURED_IMAGE_SIZE, "JPEG")

        img = Image.open(io.BytesIO(result))
        assert img.size == POST_FEATURED_IMAGE_SIZE

    def test_resize_rgba_to_jpeg(self):
        """Deve converter RGBA para RGB ao salvar como JPEG."""
        # Cria imagem RGBA
        img = Image.new("RGBA", (500, 500), color=(255, 0, 0, 128))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        content = buffer.read()

        result = resize_image(content, (200, 200), "JPEG")

        # Resultado deve ser RGB valido
        img = Image.open(io.BytesIO(result))
        assert img.mode == "RGB"
        assert img.size == (200, 200)

    def test_resize_palette_to_jpeg(self):
        """Deve converter imagem com paleta (P mode) para RGB."""
        # Cria imagem com paleta
        img = Image.new("P", (500, 500))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        content = buffer.read()

        result = resize_image(content, (200, 200), "JPEG")

        img = Image.open(io.BytesIO(result))
        assert img.mode == "RGB"

    def test_resize_preserves_quality(self):
        """Deve manter qualidade razoavel apos redimensionamento."""
        content = self.create_test_image(1000, 1000)
        result = resize_image(content, (400, 400), "JPEG")

        # Arquivo resultante deve ter tamanho razoavel
        assert len(result) > 0
        # Mas nao deve ser excessivamente grande
        assert len(result) < 500 * 1024  # < 500KB para 400x400

    def test_resize_small_image_upscales(self):
        """Imagem menor que target deve resultar em tamanho correto com padding."""
        content = self.create_test_image(100, 100)
        result = resize_image(content, (400, 400), "JPEG")

        img = Image.open(io.BytesIO(result))
        assert img.size == (400, 400)


# =============================================================================
# Testes de Integracao (Simulados)
# =============================================================================


class TestUploadIntegration:
    """Testes de integracao simulados."""

    def test_image_processing_pipeline(self):
        """Deve processar imagem completa: validar + redimensionar."""
        # Cria arquivo mock
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/jpeg"

        # Valida
        ext = validate_image(file)
        assert ext == ".jpg"

        # Cria conteudo de teste
        img = Image.new("RGB", (1000, 1000), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        content = buffer.read()

        # Redimensiona
        result = resize_image(content, CATEGORY_IMAGE_SIZE, "JPEG")

        # Verifica
        final_img = Image.open(io.BytesIO(result))
        assert final_img.size == CATEGORY_IMAGE_SIZE
        assert final_img.mode == "RGB"

    def test_post_image_open_graph_compliance(self):
        """Imagem de post deve estar no formato Open Graph (1.91:1)."""
        # Open Graph recomenda 1200x630 (ratio ~1.9:1)
        img = Image.new("RGB", (2000, 1500), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        content = buffer.read()

        result = resize_image(content, POST_FEATURED_IMAGE_SIZE, "JPEG")

        final_img = Image.open(io.BytesIO(result))
        width, height = final_img.size

        # Verifica tamanho exato Open Graph
        assert width == 1200
        assert height == 630

        # Verifica ratio aproximado (1.9:1)
        ratio = width / height
        assert 1.8 < ratio < 2.0
