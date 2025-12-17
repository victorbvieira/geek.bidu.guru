"""
Servico de geracao de imagens para posts no Instagram.

Gera imagens 1080x1080px otimizadas para feed do Instagram,
com template visual do Geek Bidu Guru incluindo:
- Pattern geek no fundo
- Logo/mascote
- Imagem do produto
- Textos estilizados (headline, titulo, preco, badge)
- Hashtags
"""

import hashlib
import math
import random
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import httpx
from PIL import Image, ImageDraw, ImageFont

from app.config import settings


# =============================================================================
# Configuracoes
# =============================================================================

# Dimensoes padrao Instagram Feed (quadrado)
IG_WIDTH = 1080
IG_HEIGHT = 1080

# Cores do tema Geek Bidu Guru (baseado no PRD-design-system.md)
COLORS = {
    # Cores principais
    "yellow_primary": "#F5B81C",     # Amarelo principal (logo, CTAs)
    "purple_dark": "#1A1A2E",        # Fundo escuro principal
    "purple_medium": "#16213E",      # Fundo gradiente
    "purple_accent": "#7C3AED",      # Roxo geek (acentos)
    "cyan_tech": "#06B6D4",          # Cyan tech (detalhes)

    # Texto
    "text_white": "#FFFFFF",         # Texto claro
    "text_gray": "#9CA3AF",          # Texto secundario

    # Neutros
    "black": "#000000",
    "white": "#FFFFFF",
}

# Diretorios
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "static" / "generated" / "instagram"
FONTS_DIR = BASE_DIR / "templates" / "instagram" / "fonts"
LOGO_PATH = BASE_DIR / "static" / "logo" / "mascot-only.png"

# Icones geek para o pattern de fundo (caracteres Unicode)
GEEK_ICONS = [
    "⚡", "🎮", "🕹️", "💻", "🖥️", "⌨️", "🖱️", "📱",
    "🎧", "🎯", "🏆", "⭐", "💎", "🔥", "✨", "👾",
    "🤖", "🚀", "💡", "🔌", "📡", "🛸", "🌟", "💫",
]


# =============================================================================
# Utilitarios
# =============================================================================


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Converte cor hexadecimal para RGB."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _get_font(
    name: str,
    size: int,
    fallback: bool = True,
) -> ImageFont.FreeTypeFont:
    """
    Obtem fonte para renderizacao.

    Args:
        name: Nome do arquivo da fonte (ex: 'Bungee-Regular.ttf')
        size: Tamanho em pixels
        fallback: Se deve usar fallback quando fonte nao encontrada

    Returns:
        Objeto ImageFont
    """
    font_path = FONTS_DIR / name

    if font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception:
            pass

    if fallback:
        # Fallback para DejaVuSans
        fallback_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        for path in fallback_paths:
            if Path(path).exists():
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue

        return ImageFont.load_default()

    raise FileNotFoundError(f"Fonte nao encontrada: {name}")


def _wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """
    Quebra texto em multiplas linhas para caber na largura maxima.

    Args:
        text: Texto a ser quebrado
        font: Fonte usada para calcular largura
        max_width: Largura maxima em pixels

    Returns:
        Lista de linhas
    """
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


async def _download_image(url: str) -> Image.Image | None:
    """
    Baixa imagem de URL externa.

    Args:
        url: URL da imagem

    Returns:
        Objeto Image ou None se falhar
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
    except Exception:
        return None


def _generate_cache_key(
    product_name: str,
    headline: str,
    title: str,
    badge_text: str,
    price: float,
) -> str:
    """Gera chave de cache baseada no conteudo."""
    content = f"{product_name}:{headline}:{title}:{badge_text}:{price}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


# =============================================================================
# Desenho de Elementos
# =============================================================================


def _draw_gradient_background(img: Image.Image) -> None:
    """
    Desenha gradiente de fundo roxo escuro.

    Gradiente vertical de purple_dark para purple_medium.
    """
    draw = ImageDraw.Draw(img)

    start_color = _hex_to_rgb(COLORS["purple_dark"])
    end_color = _hex_to_rgb(COLORS["purple_medium"])

    for y in range(IG_HEIGHT):
        ratio = y / IG_HEIGHT
        r = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
        g = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
        b = int(start_color[2] + ratio * (end_color[2] - start_color[2]))
        draw.line([(0, y), (IG_WIDTH, y)], fill=(r, g, b))


def _draw_geek_pattern(img: Image.Image) -> None:
    """
    Desenha pattern geek sutil no fundo.

    Icones geek espalhados com baixa opacidade.
    """
    # Usa seed fixo baseado na posicao para reproducibilidade
    random.seed(42)

    try:
        # Tenta usar fonte com emojis
        emoji_font = _get_font("PressStart2P-Regular.ttf", 20, fallback=False)
    except FileNotFoundError:
        # Fallback - usa caracteres simples
        emoji_font = _get_font("PressStart2P-Regular.ttf", 20, fallback=True)

    # Cria overlay com transparencia
    overlay = Image.new("RGBA", (IG_WIDTH, IG_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Grid de icones
    spacing = 100
    for x in range(0, IG_WIDTH, spacing):
        for y in range(0, IG_HEIGHT, spacing):
            # Offset aleatorio para parecer organico
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)

            # Seleciona icone aleatorio (caractere simples para compatibilidade)
            icon = random.choice(["*", "+", "o", "#", "x", ".", "~"])

            # Desenha com baixa opacidade
            draw.text(
                (x + offset_x, y + offset_y),
                icon,
                font=emoji_font,
                fill=(124, 58, 237, 25),  # purple_accent com 10% opacidade
            )

    # Compoe overlay no fundo
    img.paste(overlay, (0, 0), overlay)


def _draw_logo(img: Image.Image) -> None:
    """
    Desenha mascote no canto superior esquerdo.

    Carrega mascot-only.png e posiciona com tamanho adequado.
    """
    if not LOGO_PATH.exists():
        return

    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")

        # Redimensiona mascote para 120px de altura
        logo_height = 120
        aspect = logo.width / logo.height
        logo_width = int(logo_height * aspect)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Posiciona no canto superior esquerdo
        x = 40
        y = 40

        # Cola com transparencia
        img.paste(logo, (x, y), logo)
    except Exception:
        pass


def _draw_brand_text(draw: ImageDraw.Draw) -> None:
    """
    Desenha texto "GEEK BIDU GURU" em Bungee.

    Posicionado ao lado do mascote no topo.
    """
    font = _get_font("Bungee-Regular.ttf", 36)
    text = "GEEK BIDU GURU"

    # Posicao ao lado do mascote
    x = 180
    y = 80

    # Texto amarelo
    draw.text(
        (x, y),
        text,
        font=font,
        fill=_hex_to_rgb(COLORS["yellow_primary"]),
    )


def _draw_headline(draw: ImageDraw.Draw, headline: str) -> None:
    """
    Desenha headline de impacto no topo direito.

    Texto grande e chamativo em amarelo.
    """
    font = _get_font("Bungee-Regular.ttf", 32)

    # Quebra texto se necessario
    lines = _wrap_text(headline.upper(), font, 400)

    # Calcula posicao (alinhado a direita)
    y = 50
    for line in lines[:2]:  # Max 2 linhas
        bbox = font.getbbox(line)
        text_width = bbox[2]
        x = IG_WIDTH - text_width - 40

        draw.text(
            (x, y),
            line,
            font=font,
            fill=_hex_to_rgb(COLORS["yellow_primary"]),
        )
        y += 45


async def _draw_product_image(
    img: Image.Image,
    product_image_url: str,
) -> None:
    """
    Baixa e desenha imagem do produto no centro.

    Imagem e redimensionada e posicionada com moldura.
    """
    product_img = await _download_image(product_image_url)

    if product_img is None:
        # Desenha placeholder se imagem nao carregar
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [290, 250, 790, 700],
            fill=_hex_to_rgb(COLORS["purple_medium"]),
            outline=_hex_to_rgb(COLORS["yellow_primary"]),
            width=3,
        )
        font = _get_font("Bungee-Regular.ttf", 24)
        draw.text(
            (440, 460),
            "IMAGEM",
            font=font,
            fill=_hex_to_rgb(COLORS["text_gray"]),
        )
        return

    # Converte para RGBA se necessario
    if product_img.mode != "RGBA":
        product_img = product_img.convert("RGBA")

    # Define area para imagem do produto (quadrado central)
    max_size = 450

    # Redimensiona mantendo aspect ratio
    aspect = product_img.width / product_img.height
    if aspect > 1:
        new_width = max_size
        new_height = int(max_size / aspect)
    else:
        new_height = max_size
        new_width = int(max_size * aspect)

    product_img = product_img.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS,
    )

    # Centraliza na imagem
    x = (IG_WIDTH - new_width) // 2
    y = 280

    # Desenha borda/moldura antes da imagem
    draw = ImageDraw.Draw(img)
    padding = 10
    draw.rectangle(
        [x - padding, y - padding, x + new_width + padding, y + new_height + padding],
        outline=_hex_to_rgb(COLORS["yellow_primary"]),
        width=4,
    )

    # Cola imagem do produto
    img.paste(product_img, (x, y), product_img)


def _draw_price(draw: ImageDraw.Draw, price: float) -> None:
    """
    Desenha preco em destaque.

    Badge amarelo com preco formatado.
    """
    # Formata preco
    if price > 0:
        price_text = f"R$ {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        price_text = "VER PREÇO"

    font = _get_font("Bungee-Regular.ttf", 48)
    bbox = font.getbbox(price_text)
    text_width = bbox[2]
    text_height = bbox[3]

    # Posiciona abaixo da imagem do produto
    x = (IG_WIDTH - text_width) // 2
    y = 760

    # Fundo do badge
    padding_x = 30
    padding_y = 15
    draw.rounded_rectangle(
        [
            x - padding_x,
            y - padding_y,
            x + text_width + padding_x,
            y + text_height + padding_y,
        ],
        radius=10,
        fill=_hex_to_rgb(COLORS["yellow_primary"]),
    )

    # Texto do preco (preto para contraste)
    draw.text(
        (x, y),
        price_text,
        font=font,
        fill=_hex_to_rgb(COLORS["black"]),
    )


def _draw_badge(draw: ImageDraw.Draw, badge_text: str) -> None:
    """
    Desenha badge decorativo (ex: "NOVO NA LOJA!").

    Posicionado no canto superior da imagem do produto.
    """
    font = _get_font("PressStart2P-Regular.ttf", 14)
    text = badge_text.upper()

    bbox = font.getbbox(text)
    text_width = bbox[2]
    text_height = bbox[3]

    # Posiciona no canto superior direito da area do produto
    x = IG_WIDTH - text_width - 60
    y = 260

    # Fundo do badge
    padding_x = 15
    padding_y = 10
    draw.rounded_rectangle(
        [
            x - padding_x,
            y - padding_y,
            x + text_width + padding_x,
            y + text_height + padding_y,
        ],
        radius=5,
        fill=_hex_to_rgb(COLORS["purple_accent"]),
    )

    # Texto
    draw.text(
        (x, y),
        text,
        font=font,
        fill=_hex_to_rgb(COLORS["white"]),
    )


def _draw_title(draw: ImageDraw.Draw, title: str) -> None:
    """
    Desenha titulo do produto.

    Texto centralizado abaixo do preco.
    """
    font = _get_font("Bungee-Regular.ttf", 28)

    # Quebra texto se necessario
    lines = _wrap_text(title, font, IG_WIDTH - 80)

    # Centraliza
    y = 860
    for line in lines[:2]:  # Max 2 linhas
        bbox = font.getbbox(line)
        text_width = bbox[2]
        x = (IG_WIDTH - text_width) // 2

        draw.text(
            (x, y),
            line,
            font=font,
            fill=_hex_to_rgb(COLORS["white"]),
        )
        y += 40


def _draw_footer(draw: ImageDraw.Draw, hashtags: list[str]) -> None:
    """
    Desenha footer com URL e hashtags.

    Informacoes de contato/site na parte inferior.
    """
    # URL do site
    url_font = _get_font("PressStart2P-Regular.ttf", 12)
    url_text = "geek.bidu.guru"

    bbox = url_font.getbbox(url_text)
    text_width = bbox[2]
    x = (IG_WIDTH - text_width) // 2
    y = 960

    draw.text(
        (x, y),
        url_text,
        font=url_font,
        fill=_hex_to_rgb(COLORS["cyan_tech"]),
    )

    # Hashtags (primeiras 3 apenas para preview visual)
    if hashtags:
        hashtag_font = _get_font("PressStart2P-Regular.ttf", 10)
        hashtag_text = " ".join([f"#{h}" for h in hashtags[:3]])

        bbox = hashtag_font.getbbox(hashtag_text)
        text_width = bbox[2]
        x = (IG_WIDTH - text_width) // 2
        y = 1000

        draw.text(
            (x, y),
            hashtag_text,
            font=hashtag_font,
            fill=_hex_to_rgb(COLORS["text_gray"]),
        )


# =============================================================================
# Funcao Principal
# =============================================================================


async def generate_instagram_image(
    product_name: str,
    product_image_url: str,
    price: float,
    headline: str,
    title: str,
    badge_text: str,
    hashtags: list[str],
    use_cache: bool = True,
) -> tuple[str, int]:
    """
    Gera imagem 1080x1080 para post no Instagram.

    Args:
        product_name: Nome completo do produto (para cache)
        product_image_url: URL da imagem do produto
        price: Preco em reais (0 para "VER PREÇO")
        headline: Frase de impacto (max 25 chars)
        title: Titulo para exibicao (max 40 chars)
        badge_text: Texto do badge (max 15 chars)
        hashtags: Lista de hashtags (sem #)
        use_cache: Se deve usar cache de imagens

    Returns:
        tuple[str, int]: (caminho_relativo, tamanho_kb)

    Exemplo:
        path, size = await generate_instagram_image(
            product_name="Headset Gamer RGB",
            product_image_url="https://...",
            price=199.90,
            headline="OFERTA IMPERDÍVEL!",
            title="Headset Gamer RGB",
            badge_text="NOVO!",
            hashtags=["gamer", "headset", "rgb"],
        )
    """
    # Verifica cache
    cache_key = _generate_cache_key(product_name, headline, title, badge_text, price)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if use_cache:
        for cached_file in CACHE_DIR.glob(f"{cache_key}_*.png"):
            return f"/static/generated/instagram/{cached_file.name}", cached_file.stat().st_size // 1024

    # Cria imagem base RGBA
    img = Image.new("RGBA", (IG_WIDTH, IG_HEIGHT), _hex_to_rgb(COLORS["purple_dark"]))

    # 1. Desenha gradiente de fundo
    _draw_gradient_background(img)

    # 2. Desenha pattern geek sutil
    _draw_geek_pattern(img)

    # 3. Desenha logo/mascote
    _draw_logo(img)

    # 4. Desenha texto da marca
    draw = ImageDraw.Draw(img)
    _draw_brand_text(draw)

    # 5. Desenha headline
    _draw_headline(draw, headline)

    # 6. Desenha badge
    _draw_badge(draw, badge_text)

    # 7. Baixa e desenha imagem do produto
    await _draw_product_image(img, product_image_url)

    # Recriar draw apos modificar imagem
    draw = ImageDraw.Draw(img)

    # 8. Desenha preco
    _draw_price(draw, price)

    # 9. Desenha titulo
    _draw_title(draw, title)

    # 10. Desenha footer
    _draw_footer(draw, hashtags)

    # Converte para RGB (PNG nao precisa de alpha)
    img = img.convert("RGB")

    # Gera nome unico
    filename = f"{cache_key}_{uuid4().hex[:8]}.png"
    filepath = CACHE_DIR / filename

    # Salva imagem
    img.save(filepath, "PNG", optimize=True)

    file_size_kb = filepath.stat().st_size // 1024
    relative_path = f"/static/generated/instagram/{filename}"

    return relative_path, file_size_kb


# =============================================================================
# Utilitarios de Cache
# =============================================================================


def clear_instagram_cache() -> int:
    """
    Limpa cache de imagens Instagram.

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


def get_instagram_cache_stats() -> tuple[int, int]:
    """
    Retorna estatisticas do cache.

    Returns:
        Tupla (numero_arquivos, tamanho_total_kb)
    """
    if not CACHE_DIR.exists():
        return 0, 0

    files = list(CACHE_DIR.glob("*.png"))
    total_size = sum(f.stat().st_size for f in files) // 1024

    return len(files), total_size
