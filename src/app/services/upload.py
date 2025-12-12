"""
Servico de upload de arquivos.

Gerencia upload, validacao e armazenamento de imagens.
"""

import os
import uuid
from pathlib import Path
from typing import BinaryIO

from fastapi import HTTPException, UploadFile, status

# Tipos de arquivo permitidos
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

# Tamanho maximo: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Diretorio base de uploads
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"


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


async def save_product_image(file: UploadFile) -> str:
    """
    Salva imagem de produto.

    Args:
        file: Arquivo de imagem

    Returns:
        URL relativa da imagem salva (ex: /static/uploads/products/xxx.jpg)

    Raises:
        HTTPException: Se erro no upload
    """
    # Valida arquivo
    extension = validate_image(file)

    # Gera nome unico
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

    # Salva arquivo
    with open(upload_path, "wb") as f:
        f.write(content)

    # Retorna URL relativa
    return f"/static/uploads/products/{filename}"


def delete_product_image(image_url: str) -> bool:
    """
    Remove imagem de produto.

    Args:
        image_url: URL relativa da imagem

    Returns:
        True se removida, False se nao encontrada
    """
    if not image_url or not image_url.startswith("/static/uploads/"):
        return False

    # Converte URL para caminho
    relative_path = image_url.replace("/static/uploads/", "")
    file_path = UPLOAD_DIR / relative_path

    if file_path.exists():
        os.remove(file_path)
        return True

    return False
