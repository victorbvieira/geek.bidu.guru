"""
Validacao e processamento de uploads de arquivos.

Implementa validacao de tipo, tamanho e seguranca para uploads.
"""

from typing import Optional

from fastapi import HTTPException, UploadFile, status


# Tipos de arquivo permitidos por categoria
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/gif": [".gif"],
    "image/webp": [".webp"],
}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": [".pdf"],
    "text/plain": [".txt"],
    "text/markdown": [".md"],
}

# Limites de tamanho
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB (sera comprimido automaticamente)
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Magic bytes para verificacao de tipo real
MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
    b"RIFF": "image/webp",  # WebP comeca com RIFF
    b"%PDF": "application/pdf",
}


async def validate_image_upload(
    file: UploadFile,
    max_size: int = MAX_IMAGE_SIZE,
    allowed_types: Optional[dict] = None,
) -> bool:
    """
    Valida upload de imagem.

    Args:
        file: Arquivo enviado
        max_size: Tamanho maximo em bytes
        allowed_types: Tipos MIME permitidos (padrao: imagens comuns)

    Returns:
        True se valido

    Raises:
        HTTPException: Se arquivo invalido
    """
    if allowed_types is None:
        allowed_types = ALLOWED_IMAGE_TYPES

    # Verificar se arquivo foi enviado
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo enviado",
        )

    # Verificar extensao
    filename = file.filename.lower()
    file_ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""

    valid_extensions = []
    for extensions in allowed_types.values():
        valid_extensions.extend(extensions)

    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo nao permitido. Permitidos: {', '.join(valid_extensions)}",
        )

    # Verificar content-type declarado
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de conteudo nao permitido: {file.content_type}",
        )

    # Verificar tamanho
    file.file.seek(0, 2)  # Ir para o final
    file_size = file.file.tell()
    file.file.seek(0)  # Voltar ao inicio

    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Maximo: {max_mb:.1f}MB",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo vazio",
        )

    # Verificar magic bytes (tipo real do arquivo)
    header = await file.read(16)
    await file.seek(0)

    detected_type = None
    for magic, mime_type in MAGIC_BYTES.items():
        if header.startswith(magic):
            detected_type = mime_type
            break

    # WebP tem formato especial: RIFF....WEBP
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        detected_type = "image/webp"

    if detected_type and detected_type != file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo nao corresponde ao conteudo",
        )

    return True


async def validate_document_upload(
    file: UploadFile,
    max_size: int = MAX_DOCUMENT_SIZE,
    allowed_types: Optional[dict] = None,
) -> bool:
    """
    Valida upload de documento.

    Args:
        file: Arquivo enviado
        max_size: Tamanho maximo em bytes
        allowed_types: Tipos MIME permitidos

    Returns:
        True se valido

    Raises:
        HTTPException: Se arquivo invalido
    """
    if allowed_types is None:
        allowed_types = ALLOWED_DOCUMENT_TYPES

    return await validate_image_upload(file, max_size, allowed_types)


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo para evitar path traversal.

    Remove caracteres perigosos e limita tamanho.
    """
    import re
    import unicodedata

    # Normaliza unicode
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    # Remove path traversal
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")

    # Mantem apenas caracteres seguros
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    # Remove multiplos underscores
    filename = re.sub(r"_+", "_", filename)

    # Limita tamanho
    if len(filename) > 100:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:90] + ("." + ext if ext else "")

    return filename.strip("_")
