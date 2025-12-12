"""
Servico de geracao de imagens Open Graph dinamicas.

Gera imagens 1200x630px otimizadas para compartilhamento em redes sociais.
Suporta posts, produtos e paginas customizadas.
"""

import hashlib
from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont

from app.config import settings


# -----------------------------------------------------------------------------
# Configuracoes
# -----------------------------------------------------------------------------

# Dimensoes padrao OG (recomendado pelo Facebook/Twitter)
OG_WIDTH = 1200
OG_HEIGHT = 630

# Cores do tema (dark geek)
COLORS = {
    "bg_primary": "#020617",      # Fundo escuro
    "bg_gradient": "#0F172A",     # Fundo gradiente
    "primary": "#7C3AED",         # Roxo geek
    "secondary": "#06B6D4",       # Cyan tech
    "accent": "#FACC15",          # Amarelo CTA
    "text_primary": "#F9FAFB",    # Texto claro
    "text_secondary": "#9CA3AF",  # Texto secundario
}

# Diretorio de cache para imagens geradas
CACHE_DIR = Path(__file__).parent.parent / "static" / "og-cache"

# Diretorio de fontes
FONTS_DIR = Path(__file__).parent.parent / "static" / "fonts"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Converte cor hexadecimal para RGB."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """
    Obtem fonte para renderizacao.

    Tenta usar fontes customizadas, fallback para default.
    """
    font_names = [
        "Poppins-Bold.ttf" if bold else "Poppins-Regular.ttf",
        "Inter-Bold.ttf" if bold else "Inter-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]

    for font_name in font_names:
        font_path = FONTS_DIR / font_name
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception:
                continue

    # Fallback para fonte padrao do Pillow
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Quebra texto em multiplas linhas para caber na largura maxima."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        if bbox[2] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def _generate_cache_key(
    text: str,
    og_type: str,
    subtitle: str | None = None,
) -> str:
    """Gera chave de cache baseada no conteudo."""
    content = f"{og_type}:{text}:{subtitle or ''}"
    return hashlib.md5(content.encode()).hexdigest()


# -----------------------------------------------------------------------------
# Geradores de Imagem
# -----------------------------------------------------------------------------


def generate_og_image(
    title: str,
    og_type: Literal["post", "product", "category", "home"] = "post",
    subtitle: str | None = None,
    category: str | None = None,
    price: str | None = None,
    platform: str | None = None,
    use_cache: bool = True,
) -> bytes:
    """
    Gera imagem Open Graph dinamica.

    Args:
        title: Titulo principal (headline)
        og_type: Tipo de conteudo (post, product, category, home)
        subtitle: Subtitulo ou descricao curta
        category: Nome da categoria (para posts)
        price: Preco formatado (para produtos)
        platform: Plataforma (amazon, mercadolivre, shopee)
        use_cache: Se deve usar/salvar cache

    Returns:
        bytes da imagem PNG
    """
    # Verifica cache
    cache_key = _generate_cache_key(title, og_type, subtitle)
    cache_path = CACHE_DIR / f"{cache_key}.png"

    if use_cache and cache_path.exists():
        return cache_path.read_bytes()

    # Cria imagem base
    img = Image.new("RGB", (OG_WIDTH, OG_HEIGHT), _hex_to_rgb(COLORS["bg_primary"]))
    draw = ImageDraw.Draw(img)

    # Desenha gradiente de fundo (simulado com retangulos)
    _draw_background_gradient(draw)

    # Desenha elementos decorativos
    _draw_decorations(draw, og_type)

    # Desenha logo/marca
    _draw_branding(draw)

    # Desenha conteudo baseado no tipo
    if og_type == "product":
        _draw_product_content(draw, title, price, platform)
    elif og_type == "category":
        _draw_category_content(draw, title, subtitle)
    else:
        _draw_post_content(draw, title, subtitle, category)

    # Converte para bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    image_bytes = buffer.getvalue()

    # Salva cache
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(image_bytes)

    return image_bytes


def _draw_background_gradient(draw: ImageDraw.Draw) -> None:
    """Desenha gradiente de fundo."""
    # Gradiente vertical sutil
    for y in range(OG_HEIGHT):
        ratio = y / OG_HEIGHT
        r = int(2 + ratio * 13)   # 02 -> 0F
        g = int(6 + ratio * 17)   # 06 -> 17
        b = int(23 + ratio * 19)  # 17 -> 2A
        draw.line([(0, y), (OG_WIDTH, y)], fill=(r, g, b))


def _draw_decorations(draw: ImageDraw.Draw, og_type: str) -> None:
    """Desenha elementos decorativos."""
    # Linha superior colorida
    primary_rgb = _hex_to_rgb(COLORS["primary"])
    secondary_rgb = _hex_to_rgb(COLORS["secondary"])

    # Barra superior gradiente
    for x in range(OG_WIDTH):
        ratio = x / OG_WIDTH
        r = int(primary_rgb[0] + ratio * (secondary_rgb[0] - primary_rgb[0]))
        g = int(primary_rgb[1] + ratio * (secondary_rgb[1] - primary_rgb[1]))
        b = int(primary_rgb[2] + ratio * (secondary_rgb[2] - primary_rgb[2]))
        draw.line([(x, 0), (x, 6)], fill=(r, g, b))

    # Circulo decorativo no canto
    if og_type == "product":
        draw.ellipse(
            [OG_WIDTH - 200, -100, OG_WIDTH + 50, 150],
            fill=_hex_to_rgb(COLORS["accent"]) + (30,),
            outline=None,
        )
    else:
        draw.ellipse(
            [OG_WIDTH - 150, -50, OG_WIDTH + 100, 200],
            fill=_hex_to_rgb(COLORS["primary"]) + (20,),
            outline=None,
        )


def _draw_branding(draw: ImageDraw.Draw) -> None:
    """Desenha logo e marca."""
    # Nome do site
    font = _get_font(28, bold=True)
    text = "geek.bidu.guru"
    draw.text(
        (60, OG_HEIGHT - 60),
        text,
        font=font,
        fill=_hex_to_rgb(COLORS["text_secondary"]),
    )


def _draw_post_content(
    draw: ImageDraw.Draw,
    title: str,
    subtitle: str | None,
    category: str | None,
) -> None:
    """Desenha conteudo para posts."""
    y_offset = 120

    # Categoria (badge)
    if category:
        cat_font = _get_font(20, bold=True)
        cat_text = category.upper()
        draw.text(
            (60, y_offset),
            cat_text,
            font=cat_font,
            fill=_hex_to_rgb(COLORS["primary"]),
        )
        y_offset += 50

    # Titulo
    title_font = _get_font(56, bold=True)
    title_lines = _wrap_text(title, title_font, OG_WIDTH - 120)

    for i, line in enumerate(title_lines[:3]):  # Max 3 linhas
        draw.text(
            (60, y_offset + i * 70),
            line,
            font=title_font,
            fill=_hex_to_rgb(COLORS["text_primary"]),
        )

    y_offset += len(title_lines[:3]) * 70 + 30

    # Subtitulo
    if subtitle:
        sub_font = _get_font(28)
        sub_lines = _wrap_text(subtitle, sub_font, OG_WIDTH - 120)

        for i, line in enumerate(sub_lines[:2]):  # Max 2 linhas
            draw.text(
                (60, y_offset + i * 40),
                line,
                font=sub_font,
                fill=_hex_to_rgb(COLORS["text_secondary"]),
            )


def _draw_product_content(
    draw: ImageDraw.Draw,
    title: str,
    price: str | None,
    platform: str | None,
) -> None:
    """Desenha conteudo para produtos."""
    y_offset = 150

    # Plataforma (badge)
    if platform:
        platform_colors = {
            "amazon": "#FF9900",
            "mercadolivre": "#FFE600",
            "shopee": "#EE4D2D",
        }
        badge_color = platform_colors.get(platform.lower(), COLORS["primary"])

        plat_font = _get_font(18, bold=True)
        plat_text = platform.upper()

        # Desenha badge
        bbox = plat_font.getbbox(plat_text)
        badge_width = bbox[2] + 24
        badge_height = 32

        draw.rounded_rectangle(
            [60, y_offset, 60 + badge_width, y_offset + badge_height],
            radius=4,
            fill=_hex_to_rgb(badge_color),
        )
        draw.text(
            (72, y_offset + 6),
            plat_text,
            font=plat_font,
            fill=(0, 0, 0) if platform.lower() in ["amazon", "mercadolivre"] else (255, 255, 255),
        )
        y_offset += 60

    # Titulo
    title_font = _get_font(48, bold=True)
    title_lines = _wrap_text(title, title_font, OG_WIDTH - 120)

    for i, line in enumerate(title_lines[:3]):
        draw.text(
            (60, y_offset + i * 60),
            line,
            font=title_font,
            fill=_hex_to_rgb(COLORS["text_primary"]),
        )

    y_offset += len(title_lines[:3]) * 60 + 40

    # Preco
    if price:
        price_font = _get_font(52, bold=True)
        draw.text(
            (60, y_offset),
            price,
            font=price_font,
            fill=_hex_to_rgb(COLORS["accent"]),
        )


def _draw_category_content(
    draw: ImageDraw.Draw,
    title: str,
    subtitle: str | None,
) -> None:
    """Desenha conteudo para categorias."""
    y_offset = 180

    # Label
    label_font = _get_font(24, bold=True)
    draw.text(
        (60, y_offset),
        "CATEGORIA",
        font=label_font,
        fill=_hex_to_rgb(COLORS["secondary"]),
    )
    y_offset += 50

    # Titulo
    title_font = _get_font(64, bold=True)
    title_lines = _wrap_text(title, title_font, OG_WIDTH - 120)

    for i, line in enumerate(title_lines[:2]):
        draw.text(
            (60, y_offset + i * 80),
            line,
            font=title_font,
            fill=_hex_to_rgb(COLORS["text_primary"]),
        )

    y_offset += len(title_lines[:2]) * 80 + 30

    # Descricao
    if subtitle:
        sub_font = _get_font(28)
        sub_lines = _wrap_text(subtitle, sub_font, OG_WIDTH - 120)

        for i, line in enumerate(sub_lines[:2]):
            draw.text(
                (60, y_offset + i * 40),
                line,
                font=sub_font,
                fill=_hex_to_rgb(COLORS["text_secondary"]),
            )


# -----------------------------------------------------------------------------
# Limpeza de Cache
# -----------------------------------------------------------------------------


def clear_og_cache() -> int:
    """
    Limpa cache de imagens OG.

    Returns:
        Numero de arquivos removidos
    """
    if not CACHE_DIR.exists():
        return 0

    count = 0
    for file in CACHE_DIR.glob("*.png"):
        file.unlink()
        count += 1

    return count


def get_og_cache_size() -> tuple[int, int]:
    """
    Retorna estatisticas do cache.

    Returns:
        Tupla (numero_arquivos, tamanho_total_bytes)
    """
    if not CACHE_DIR.exists():
        return 0, 0

    files = list(CACHE_DIR.glob("*.png"))
    total_size = sum(f.stat().st_size for f in files)

    return len(files), total_size
