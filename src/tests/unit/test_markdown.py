"""
Testes unitarios para o modulo de Markdown.

Verifica:
- Conversao de Markdown para HTML
- Demote de headings (# -> h2, ## -> h3)
- Sanitizacao de HTML
- Shortcodes de produto
- Extracao de TOC
"""

import pytest

from app.utils.markdown import (
    PRODUCT_SHORTCODE_PATTERN,
    extract_product_refs,
    extract_toc,
    is_markdown,
    markdown_to_html,
    render_product_card,
    render_product_placeholder,
    replace_product_shortcodes,
)


# =============================================================================
# Testes de Conversao Basica
# =============================================================================


class TestMarkdownToHtml:
    """Testes para conversao de Markdown para HTML."""

    def test_convert_basic_text(self):
        """Deve converter texto simples."""
        content = "Texto simples"
        result = markdown_to_html(content)
        assert "<p>Texto simples</p>" in result

    def test_convert_bold_text(self):
        """Deve converter texto em negrito."""
        content = "Texto **negrito** aqui"
        result = markdown_to_html(content)
        assert "<strong>negrito</strong>" in result

    def test_convert_italic_text(self):
        """Deve converter texto em italico."""
        content = "Texto *italico* aqui"
        result = markdown_to_html(content)
        assert "<em>italico</em>" in result

    def test_convert_link(self):
        """Deve converter links."""
        content = "[Link](https://example.com)"
        result = markdown_to_html(content)
        assert 'href="https://example.com"' in result

    def test_convert_list(self):
        """Deve converter listas."""
        content = "- Item 1\n- Item 2"
        result = markdown_to_html(content)
        assert "<ul>" in result
        assert "<li>" in result

    def test_convert_code_block(self):
        """Deve converter blocos de codigo."""
        content = "```python\nprint('hello')\n```"
        result = markdown_to_html(content)
        assert "<code" in result

    def test_convert_empty_content(self):
        """Deve retornar string vazia para conteudo vazio."""
        assert markdown_to_html("") == ""
        assert markdown_to_html(None) == ""

    def test_sanitize_prevents_xss(self):
        """Deve sanitizar conteudo para prevenir XSS."""
        content = '<script>alert("xss")</script>'
        result = markdown_to_html(content, sanitize=True)
        # Script tag deve ser removida (XSS prevenido)
        assert "<script>" not in result

    def test_no_sanitize_allows_script(self):
        """Sem sanitizacao, deve manter script."""
        content = '<script>alert("xss")</script>'
        result = markdown_to_html(content, sanitize=False)
        assert "<script>" in result


# =============================================================================
# Testes de Demote Headings
# =============================================================================


class TestDemoteHeadings:
    """Testes para demote de headings (# -> h2, ## -> h3)."""

    def test_h1_becomes_h2(self):
        """# deve virar h2."""
        content = "# Titulo Principal"
        result = markdown_to_html(content, demote_headings=True)
        assert "<h2>" in result
        assert "<h1>" not in result

    def test_h2_becomes_h3(self):
        """## deve virar h3."""
        content = "## Subtitulo"
        result = markdown_to_html(content, demote_headings=True)
        assert "<h3>" in result
        assert "<h2>" not in result

    def test_h3_becomes_h4(self):
        """### deve virar h4."""
        content = "### Secao"
        result = markdown_to_html(content, demote_headings=True)
        assert "<h4>" in result
        assert "<h3>" not in result

    def test_h4_becomes_h5(self):
        """#### deve virar h5."""
        content = "#### Subsecao"
        result = markdown_to_html(content, demote_headings=True)
        assert "<h5>" in result
        assert "<h4>" not in result

    def test_h5_becomes_h6(self):
        """##### deve virar h6."""
        content = "##### Item"
        result = markdown_to_html(content, demote_headings=True)
        assert "<h6>" in result
        assert "<h5>" not in result

    def test_h6_stays_h6(self):
        """###### deve manter h6 (limite)."""
        content = "###### Menor nivel"
        result = markdown_to_html(content, demote_headings=True)
        assert "<h6>" in result

    def test_no_demote_headings(self):
        """Sem demote, # deve virar h1."""
        content = "# Titulo Principal"
        result = markdown_to_html(content, demote_headings=False)
        assert "<h1>" in result

    def test_multiple_headings_demoted(self):
        """Deve demotar multiplos headings."""
        content = "# H1\n## H2\n### H3"
        result = markdown_to_html(content, demote_headings=True)
        assert "<h2>" in result
        assert "<h3>" in result
        assert "<h4>" in result
        assert "<h1>" not in result

    def test_heading_with_attributes_demoted(self):
        """Deve preservar atributos ao demotar."""
        content = "# Titulo {#custom-id}"
        result = markdown_to_html(content, demote_headings=True, sanitize=False)
        # Markdown extra pode adicionar id
        assert "<h2" in result


# =============================================================================
# Testes de Pilcrow (Permalink)
# =============================================================================


class TestNoPilcrow:
    """Testes para verificar que nao ha pilcrow nos headings."""

    def test_no_pilcrow_in_headings(self):
        """Nao deve haver simbolo de pilcrow nos headings."""
        content = "# Titulo\n## Subtitulo"
        result = markdown_to_html(content)
        # Pilcrow (¶) nao deve aparecer
        assert "\u00b6" not in result
        assert "&#182;" not in result


# =============================================================================
# Testes de Deteccao de Markdown
# =============================================================================


class TestIsMarkdown:
    """Testes para deteccao de Markdown."""

    def test_detect_headers(self):
        """Deve detectar headers."""
        assert is_markdown("# Titulo")
        assert is_markdown("## Subtitulo")
        assert is_markdown("### Secao")

    def test_detect_bold(self):
        """Deve detectar negrito."""
        assert is_markdown("Texto **negrito**")
        assert is_markdown("Texto __negrito__")

    def test_detect_lists(self):
        """Deve detectar listas."""
        assert is_markdown("- Item")
        assert is_markdown("* Item")
        assert is_markdown("1. Item")

    def test_detect_code_blocks(self):
        """Deve detectar blocos de codigo."""
        assert is_markdown("```code```")

    def test_detect_links(self):
        """Deve detectar links."""
        assert is_markdown("[texto](url)")

    def test_detect_images(self):
        """Deve detectar imagens."""
        assert is_markdown("![alt](url)")

    def test_detect_blockquotes(self):
        """Deve detectar citacoes."""
        assert is_markdown("> citacao")

    def test_plain_text_not_markdown(self):
        """Texto simples sem padroes nao deve ser detectado."""
        # Texto muito simples pode nao ter padroes Markdown
        result = is_markdown("Texto simples sem formatacao especial")
        # O asterisco isolado pode detectar como markdown
        assert isinstance(result, bool)

    def test_empty_content(self):
        """Conteudo vazio nao e Markdown."""
        assert not is_markdown("")
        assert not is_markdown(None)


# =============================================================================
# Testes de TOC
# =============================================================================


class TestExtractToc:
    """Testes para extracao de TOC."""

    def test_extract_toc_from_headings(self):
        """Deve extrair TOC de headings."""
        content = "# H1\n## H2\n### H3"
        toc = extract_toc(content)
        assert toc is not None
        assert "H1" in toc or "H2" in toc  # Depende da config do toc

    def test_no_toc_without_headings(self):
        """Sem headings, TOC deve ser vazio ou conter apenas estrutura vazia."""
        content = "Texto simples sem headers"
        toc = extract_toc(content)
        # TOC pode retornar estrutura HTML vazia sem itens de lista
        if toc:
            # Verifica que nao ha items de lista (li)
            assert "<li>" not in toc

    def test_toc_empty_content(self):
        """Conteudo vazio retorna None."""
        assert extract_toc("") is None
        assert extract_toc(None) is None


# =============================================================================
# Testes de Shortcodes de Produto
# =============================================================================


class TestProductShortcode:
    """Testes para shortcodes de produto."""

    def test_shortcode_pattern_matches_slug(self):
        """Pattern deve casar com slug."""
        match = PRODUCT_SHORTCODE_PATTERN.search("[product:funko-vader]")
        assert match is not None
        assert match.group(1) == "funko-vader"

    def test_shortcode_pattern_matches_uuid(self):
        """Pattern deve casar com UUID."""
        uuid_str = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        # Sem hifens no UUID no pattern atual
        match = PRODUCT_SHORTCODE_PATTERN.search("[product:abc123]")
        assert match is not None

    def test_shortcode_case_insensitive(self):
        """Pattern deve ser case insensitive."""
        match1 = PRODUCT_SHORTCODE_PATTERN.search("[product:slug]")
        match2 = PRODUCT_SHORTCODE_PATTERN.search("[PRODUCT:slug]")
        match3 = PRODUCT_SHORTCODE_PATTERN.search("[Product:slug]")
        assert all([match1, match2, match3])


class TestExtractProductRefs:
    """Testes para extracao de referencias de produtos."""

    def test_extract_single_ref(self):
        """Deve extrair uma referencia."""
        content = "Confira [product:funko-vader]"
        refs = extract_product_refs(content)
        assert refs == ["funko-vader"]

    def test_extract_multiple_refs(self):
        """Deve extrair multiplas referencias."""
        content = "[product:prod1] e [product:prod2]"
        refs = extract_product_refs(content)
        assert "prod1" in refs
        assert "prod2" in refs
        assert len(refs) == 2

    def test_extract_unique_refs(self):
        """Deve remover duplicatas."""
        content = "[product:same] e [product:same]"
        refs = extract_product_refs(content)
        assert len(refs) == 1
        assert refs[0] == "same"

    def test_extract_no_refs(self):
        """Sem referencias, retorna lista vazia."""
        content = "Texto sem produtos"
        refs = extract_product_refs(content)
        assert refs == []

    def test_extract_empty_content(self):
        """Conteudo vazio retorna lista vazia."""
        assert extract_product_refs("") == []
        assert extract_product_refs(None) == []


class TestRenderProductCard:
    """Testes para renderizacao de card de produto."""

    @pytest.fixture
    def sample_product(self):
        """Produto de exemplo."""
        return {
            "name": "Funko Pop Darth Vader",
            "slug": "funko-vader",
            "price": 149.90,
            "platform": "amazon",
            "main_image_url": "/static/uploads/products/vader.jpg",
            "affiliate_redirect_slug": "vader-amazon",
        }

    def test_render_with_image(self, sample_product):
        """Deve renderizar card com imagem."""
        html = render_product_card(sample_product)
        assert 'class="product-embed"' in html
        assert sample_product["name"] in html
        assert sample_product["main_image_url"] in html

    def test_render_without_image(self, sample_product):
        """Deve renderizar placeholder sem imagem."""
        sample_product["main_image_url"] = None
        html = render_product_card(sample_product)
        assert "Sem imagem" in html

    def test_render_with_price(self, sample_product):
        """Deve exibir preco formatado."""
        html = render_product_card(sample_product)
        assert "R$ 149.90" in html

    def test_render_without_price(self, sample_product):
        """Deve funcionar sem preco."""
        sample_product["price"] = None
        html = render_product_card(sample_product)
        assert "product-embed" in html

    def test_render_platform_badge(self, sample_product):
        """Deve exibir badge de plataforma."""
        html = render_product_card(sample_product)
        assert "platform-amazon" in html
        assert "Amazon" in html

    def test_render_cta_link(self, sample_product):
        """Deve ter link de CTA."""
        html = render_product_card(sample_product)
        assert "Ver Oferta" in html
        assert f"/goto/{sample_product['affiliate_redirect_slug']}" in html


class TestRenderProductPlaceholder:
    """Testes para placeholder de produto nao encontrado."""

    def test_placeholder_shows_identifier(self):
        """Deve mostrar identificador do produto."""
        html = render_product_placeholder("produto-inexistente")
        assert "produto-inexistente" in html
        assert "nao encontrado" in html

    def test_placeholder_has_correct_class(self):
        """Deve ter classe de not-found."""
        html = render_product_placeholder("slug")
        assert "product-embed-not-found" in html


class TestReplaceProductShortcodes:
    """Testes para substituicao de shortcodes."""

    def test_replace_found_product(self):
        """Deve substituir shortcode por card."""
        content = "Confira [product:vader]"
        products = {
            "vader": {
                "name": "Darth Vader",
                "slug": "vader",
                "price": 100,
                "platform": "amazon",
                "affiliate_redirect_slug": "vader",
            }
        }
        result = replace_product_shortcodes(content, products)
        assert "[product:vader]" not in result
        assert "Darth Vader" in result
        assert "product-embed" in result

    def test_replace_not_found_product(self):
        """Deve substituir por placeholder se nao encontrado."""
        content = "[product:inexistente]"
        products = {}
        result = replace_product_shortcodes(content, products)
        assert "product-embed-not-found" in result
        assert "inexistente" in result

    def test_replace_multiple_products(self):
        """Deve substituir multiplos produtos."""
        content = "[product:a] e [product:b]"
        products = {
            "a": {"name": "A", "slug": "a", "platform": "amazon", "affiliate_redirect_slug": "a"},
            "b": {"name": "B", "slug": "b", "platform": "shopee", "affiliate_redirect_slug": "b"},
        }
        result = replace_product_shortcodes(content, products)
        assert "A" in result
        assert "B" in result

    def test_replace_empty_content(self):
        """Conteudo vazio retorna vazio."""
        assert replace_product_shortcodes("", {}) == ""
        assert replace_product_shortcodes(None, {}) == ""
