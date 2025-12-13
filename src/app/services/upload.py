"""
Servico de upload de arquivos.

Gerencia upload, validacao e armazenamento de imagens.

IMPORTANTE: Em producao, configure UPLOAD_DIR via variavel de ambiente
para usar um volume persistente (ex: /app/uploads).
"""

import io
import os
import uuid
from pathlib import Path
from typing import BinaryIO, Optional, Tuple

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.config import settings

# Tipos de arquivo permitidos
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

# Tamanho maximo: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# =============================================================================
# Padroes de tamanho de imagens
# =============================================================================

# Categorias: 400x400 px (1:1) - Usado em cards e listagens
CATEGORY_IMAGE_SIZE = (400, 400)

# Produtos: diferentes tamanhos para diferentes usos
PRODUCT_IMAGE_SIZES = {
    "main": (800, 800),    # Imagem principal na pagina do produto
    "thumb": (200, 200),   # Thumbnail para listagens
}

# Posts: 1200x630 px (1.91:1) - Padrao Open Graph para redes sociais
POST_FEATURED_IMAGE_SIZE = (1200, 630)

# Qualidade JPEG (0-100)
IMAGE_QUALITY = 85

# Diretorio base de uploads
# Em producao: use UPLOAD_DIR=/app/uploads com volume Docker persistente
# Em desenvolvimento: usa o diretorio padrao dentro do projeto
if settings.upload_dir:
    UPLOAD_DIR = Path(settings.upload_dir)
    # Em producao com diretorio externo, usa /uploads/ como prefixo de URL
    UPLOAD_URL_PREFIX = "/uploads"
else:
    UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"
    # Em desenvolvimento, usa /static/uploads/ (servido automaticamente pelo FastAPI)
    UPLOAD_URL_PREFIX = "/static/uploads"


def get_upload_url(subdir: str, filename: str) -> str:
    """
    Retorna a URL para acessar um arquivo de upload.

    Args:
        subdir: Subdiretorio (products, categories, posts)
        filename: Nome do arquivo

    Returns:
        URL relativa para o arquivo
    """
    return f"{UPLOAD_URL_PREFIX}/{subdir}/{filename}"


def validate_image(file: UploadFile) -> str:
    """
    Valida arquivo de imagem.

    Args:
        file: Arquivo enviado

    Returns:
        Extensao do arquivo

    Raises:
        HTTPException: Se arquivo invalido
    """
    # Verifica content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo nao permitido: {file.content_type}. "
            f"Tipos aceitos: {', '.join(ALLOWED_IMAGE_TYPES.keys())}",
        )

    return ALLOWED_IMAGE_TYPES[file.content_type]


async def save_product_image(file: UploadFile, resize: bool = False) -> str:
    """
    Salva imagem de produto.

    Args:
        file: Arquivo de imagem
        resize: Se True, redimensiona para 800x800 (padrao do projeto)

    Returns:
        URL relativa da imagem salva (ex: /static/uploads/products/xxx.jpg)

    Raises:
        HTTPException: Se erro no upload
    """
    # Valida arquivo
    extension = validate_image(file)

    # Se vai redimensionar, sempre salva como .jpg
    if resize:
        filename = f"{uuid.uuid4().hex}.jpg"
    else:
        filename = f"{uuid.uuid4().hex}{extension}"

    # Caminho completo
    upload_path = UPLOAD_DIR / "products" / filename

    # Garante que diretorio existe
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    # Le conteudo e valida tamanho
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Tamanho maximo: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Redimensiona se solicitado
    if resize:
        content = resize_image(content, PRODUCT_IMAGE_SIZES["main"], "JPEG")

    # Salva arquivo
    with open(upload_path, "wb") as f:
        f.write(content)

    # Retorna URL relativa
    return get_upload_url("products", filename)


def delete_product_image(image_url: str) -> bool:
    """
    Remove imagem de produto.

    Args:
        image_url: URL relativa da imagem

    Returns:
        True se removida, False se nao encontrada
    """
    if not image_url:
        return False

    # Suporta ambos os prefixos (para migracoes)
    if image_url.startswith("/static/uploads/"):
        relative_path = image_url.replace("/static/uploads/", "")
    elif image_url.startswith("/uploads/"):
        relative_path = image_url.replace("/uploads/", "")
    else:
        return False

    # Converte URL para caminho
    file_path = UPLOAD_DIR / relative_path

    if file_path.exists():
        os.remove(file_path)
        return True

    return False


def resize_image(
    content: bytes,
    target_size: Tuple[int, int],
    output_format: str = "JPEG",
) -> bytes:
    """
    Redimensiona imagem mantendo proporcao e preenchendo com fundo branco.

    Args:
        content: Bytes da imagem original
        target_size: Tupla (largura, altura) do tamanho final
        output_format: Formato de saida (JPEG, PNG, WEBP)

    Returns:
        Bytes da imagem redimensionada
    """
    # Abre imagem
    img = Image.open(io.BytesIO(content))

    # Converte para RGB se necessario (para JPEG)
    if img.mode in ("RGBA", "P") and output_format == "JPEG":
        # Cria fundo branco
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB" and output_format == "JPEG":
        img = img.convert("RGB")

    # Calcula proporcao mantendo aspect ratio
    img.thumbnail(target_size, Image.Resampling.LANCZOS)

    # Cria imagem final com tamanho exato e fundo branco
    final_img = Image.new("RGB", target_size, (255, 255, 255))

    # Centraliza a imagem redimensionada
    offset = ((target_size[0] - img.size[0]) // 2, (target_size[1] - img.size[1]) // 2)
    final_img.paste(img, offset)

    # Salva em bytes
    output = io.BytesIO()
    final_img.save(output, format=output_format, quality=IMAGE_QUALITY, optimize=True)
    output.seek(0)

    return output.read()


async def save_category_image(file: UploadFile) -> str:
    """
    Salva imagem de categoria com redimensionamento padronizado.

    A imagem e redimensionada para 400x400 px mantendo proporcao
    e preenchendo com fundo branco se necessario.

    Args:
        file: Arquivo de imagem

    Returns:
        URL relativa da imagem salva (ex: /static/uploads/categories/xxx.jpg)

    Raises:
        HTTPException: Se erro no upload
    """
    # Valida arquivo (extensao ignorada pois sempre salvamos como .jpg)
    validate_image(file)

    # Gera nome unico - sempre salva como .jpg apos processamento
    filename = f"{uuid.uuid4().hex}.jpg"

    # Caminho completo
    upload_path = UPLOAD_DIR / "categories" / filename

    # Garante que diretorio existe
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    # Le conteudo e valida tamanho
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Tamanho maximo: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Redimensiona imagem para tamanho padrao
    resized_content = resize_image(content, CATEGORY_IMAGE_SIZE, "JPEG")

    # Salva arquivo
    with open(upload_path, "wb") as f:
        f.write(resized_content)

    # Retorna URL relativa
    return get_upload_url("categories", filename)


async def save_post_image(file: UploadFile) -> str:
    """
    Salva imagem de destaque de post com redimensionamento padronizado.

    A imagem e redimensionada para 1200x630 px (padrao Open Graph)
    mantendo proporcao e preenchendo com fundo branco se necessario.

    Args:
        file: Arquivo de imagem

    Returns:
        URL relativa da imagem salva (ex: /static/uploads/posts/xxx.jpg)

    Raises:
        HTTPException: Se erro no upload
    """
    # Valida arquivo (extensao ignorada pois sempre salvamos como .jpg)
    validate_image(file)

    # Gera nome unico - sempre salva como .jpg apos processamento
    filename = f"{uuid.uuid4().hex}.jpg"

    # Caminho completo
    upload_path = UPLOAD_DIR / "posts" / filename

    # Garante que diretorio existe
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    # Le conteudo e valida tamanho
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Tamanho maximo: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Redimensiona imagem para tamanho padrao Open Graph
    resized_content = resize_image(content, POST_FEATURED_IMAGE_SIZE, "JPEG")

    # Salva arquivo
    with open(upload_path, "wb") as f:
        f.write(resized_content)

    # Retorna URL relativa
    return get_upload_url("posts", filename)


def delete_category_image(image_url: str) -> bool:
    """
    Remove imagem de categoria.

    Args:
        image_url: URL relativa da imagem

    Returns:
        True se removida, False se nao encontrada
    """
    if not image_url:
        return False

    # Suporta ambos os prefixos (para migracoes)
    if image_url.startswith("/static/uploads/"):
        relative_path = image_url.replace("/static/uploads/", "")
    elif image_url.startswith("/uploads/"):
        relative_path = image_url.replace("/uploads/", "")
    else:
        return False

    # Converte URL para caminho
    file_path = UPLOAD_DIR / relative_path

    if file_path.exists():
        os.remove(file_path)
        return True

    return False
