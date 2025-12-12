/**
 * Analytics Helper - geek.bidu.guru
 *
 * Funcoes utilitarias para tracking de eventos no Google Analytics 4.
 * Inclui eventos customizados para afiliados, share, scroll, etc.
 */

// Namespace para evitar conflitos
window.GeekAnalytics = (function() {
    'use strict';

    // -------------------------------------------------------------------------
    // Configuracao
    // -------------------------------------------------------------------------

    const config = {
        debug: false,  // Ativar logs no console
        scrollThresholds: [25, 50, 75, 90, 100],  // Percentuais de scroll
        scrollTracked: new Set(),  // Evita eventos duplicados
    };

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /**
     * Log debug se ativado
     */
    function log(...args) {
        if (config.debug) {
            console.log('[GeekAnalytics]', ...args);
        }
    }

    /**
     * Verifica se gtag esta disponivel
     */
    function isGtagAvailable() {
        return typeof gtag === 'function';
    }

    /**
     * Envia evento para GA4
     */
    function sendEvent(eventName, params = {}) {
        if (!isGtagAvailable()) {
            log('gtag nao disponivel, evento ignorado:', eventName, params);
            return false;
        }

        gtag('event', eventName, params);
        log('Evento enviado:', eventName, params);
        return true;
    }

    // -------------------------------------------------------------------------
    // Eventos de Afiliados
    // -------------------------------------------------------------------------

    /**
     * Rastreia clique em link de afiliado
     * @param {string} productId - ID do produto
     * @param {string} productName - Nome do produto
     * @param {string} platform - Plataforma (amazon, mercadolivre, shopee)
     * @param {string} source - Origem do clique (post_page, product_page, home, etc)
     */
    function trackAffiliateClick(productId, productName, platform, source = 'unknown') {
        return sendEvent('affiliate_click', {
            product_id: productId,
            product_name: productName,
            affiliate_platform: platform,
            click_source: source,
            // Parametros padrao GA4
            currency: 'BRL',
            items: [{
                item_id: productId,
                item_name: productName,
                affiliation: platform,
            }]
        });
    }

    /**
     * Rastreia visualizacao de produto
     * @param {string} productId - ID do produto
     * @param {string} productName - Nome do produto
     * @param {number} price - Preco do produto
     * @param {string} platform - Plataforma
     */
    function trackProductView(productId, productName, price, platform) {
        return sendEvent('view_item', {
            currency: 'BRL',
            value: price || 0,
            items: [{
                item_id: productId,
                item_name: productName,
                affiliation: platform,
                price: price || 0,
            }]
        });
    }

    // -------------------------------------------------------------------------
    // Eventos de Compartilhamento
    // -------------------------------------------------------------------------

    /**
     * Rastreia compartilhamento de conteudo
     * @param {string} method - Metodo (whatsapp, telegram, x, facebook, linkedin, copy)
     * @param {string} contentType - Tipo (post, product, category)
     * @param {string} itemId - ID ou URL do item
     */
    function trackShare(method, contentType, itemId) {
        return sendEvent('share', {
            method: method,
            content_type: contentType,
            item_id: itemId,
        });
    }

    // -------------------------------------------------------------------------
    // Eventos de Scroll
    // -------------------------------------------------------------------------

    /**
     * Rastreia profundidade de scroll
     * @param {number} percent - Percentual scrollado (25, 50, 75, 90, 100)
     */
    function trackScrollDepth(percent) {
        // Evita enviar evento duplicado
        if (config.scrollTracked.has(percent)) {
            return false;
        }

        config.scrollTracked.add(percent);
        return sendEvent('scroll_depth', {
            percent_scrolled: percent,
            page_location: window.location.pathname,
        });
    }

    /**
     * Inicializa tracking automatico de scroll
     */
    function initScrollTracking() {
        let ticking = false;

        function checkScrollDepth() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = Math.round((scrollTop / docHeight) * 100);

            config.scrollThresholds.forEach(threshold => {
                if (scrollPercent >= threshold) {
                    trackScrollDepth(threshold);
                }
            });

            ticking = false;
        }

        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(checkScrollDepth);
                ticking = true;
            }
        }, { passive: true });

        log('Scroll tracking iniciado');
    }

    // -------------------------------------------------------------------------
    // Eventos de Engajamento
    // -------------------------------------------------------------------------

    /**
     * Rastreia visualizacao de post
     * @param {string} postId - ID do post
     * @param {string} postTitle - Titulo do post
     * @param {string} category - Categoria
     * @param {string} author - Autor
     */
    function trackPostView(postId, postTitle, category, author) {
        return sendEvent('view_content', {
            content_type: 'post',
            content_id: postId,
            content_title: postTitle,
            content_category: category,
            content_author: author,
        });
    }

    /**
     * Rastreia inscricao na newsletter
     * @param {string} location - Local do formulario (footer, popup, inline)
     */
    function trackNewsletterSignup(location = 'unknown') {
        return sendEvent('newsletter_signup', {
            form_location: location,
        });
    }

    /**
     * Rastreia busca no site
     * @param {string} searchTerm - Termo buscado
     * @param {number} resultsCount - Numero de resultados
     */
    function trackSearch(searchTerm, resultsCount) {
        return sendEvent('search', {
            search_term: searchTerm,
            results_count: resultsCount,
        });
    }

    /**
     * Rastreia clique em CTA
     * @param {string} ctaText - Texto do botao
     * @param {string} ctaLocation - Local do CTA
     * @param {string} destination - URL de destino
     */
    function trackCTAClick(ctaText, ctaLocation, destination) {
        return sendEvent('cta_click', {
            cta_text: ctaText,
            cta_location: ctaLocation,
            destination_url: destination,
        });
    }

    // -------------------------------------------------------------------------
    // Eventos de Erro
    // -------------------------------------------------------------------------

    /**
     * Rastreia erros JavaScript
     * @param {string} message - Mensagem de erro
     * @param {string} source - Arquivo fonte
     * @param {number} line - Linha do erro
     */
    function trackError(message, source, line) {
        return sendEvent('javascript_error', {
            error_message: message,
            error_source: source,
            error_line: line,
        });
    }

    /**
     * Inicializa tracking global de erros
     */
    function initErrorTracking() {
        window.addEventListener('error', function(event) {
            trackError(event.message, event.filename, event.lineno);
        });
        log('Error tracking iniciado');
    }

    // -------------------------------------------------------------------------
    // Inicializacao
    // -------------------------------------------------------------------------

    /**
     * Inicializa todos os trackings automaticos
     */
    function init(options = {}) {
        config.debug = options.debug || false;

        // Scroll tracking
        if (options.scroll !== false) {
            initScrollTracking();
        }

        // Error tracking
        if (options.errors !== false) {
            initErrorTracking();
        }

        // Auto-track affiliate clicks
        if (options.affiliates !== false) {
            initAffiliateClickTracking();
        }

        // Auto-track share buttons
        if (options.share !== false) {
            initShareTracking();
        }

        log('GeekAnalytics iniciado', config);
    }

    /**
     * Auto-tracking de cliques em links de afiliados
     */
    function initAffiliateClickTracking() {
        document.addEventListener('click', function(event) {
            const link = event.target.closest('a[href*="/goto/"]');
            if (!link) return;

            const productId = link.dataset.productId || 'unknown';
            const productName = link.dataset.productName || link.textContent.trim();
            const platform = link.dataset.platform || 'unknown';
            const source = link.dataset.source || detectSource();

            trackAffiliateClick(productId, productName, platform, source);
        });
        log('Affiliate click tracking iniciado');
    }

    /**
     * Auto-tracking de botoes de share
     */
    function initShareTracking() {
        document.addEventListener('click', function(event) {
            const shareBtn = event.target.closest('.share-btn');
            if (!shareBtn) return;

            const container = shareBtn.closest('.share-buttons');
            const method = shareBtn.classList[1]?.replace('share-', '') || 'unknown';
            const url = container?.dataset.shareUrl || window.location.href;
            const contentType = detectContentType();

            trackShare(method, contentType, url);
        });
        log('Share tracking iniciado');
    }

    /**
     * Detecta tipo de conteudo da pagina atual
     */
    function detectContentType() {
        const path = window.location.pathname;
        if (path.startsWith('/blog/') || path.startsWith('/post/')) return 'post';
        if (path.startsWith('/produto/') || path.startsWith('/products/')) return 'product';
        if (path.startsWith('/categoria/')) return 'category';
        return 'page';
    }

    /**
     * Detecta origem do clique
     */
    function detectSource() {
        const path = window.location.pathname;
        if (path === '/') return 'home';
        if (path.startsWith('/blog/')) return 'post_page';
        if (path.startsWith('/produto/')) return 'product_page';
        if (path.startsWith('/categoria/')) return 'category_page';
        if (path.startsWith('/busca')) return 'search_results';
        return 'other';
    }

    // -------------------------------------------------------------------------
    // API Publica
    // -------------------------------------------------------------------------

    return {
        init: init,
        config: config,

        // Eventos de afiliados
        trackAffiliateClick: trackAffiliateClick,
        trackProductView: trackProductView,

        // Eventos de share
        trackShare: trackShare,

        // Eventos de scroll
        trackScrollDepth: trackScrollDepth,

        // Eventos de engajamento
        trackPostView: trackPostView,
        trackNewsletterSignup: trackNewsletterSignup,
        trackSearch: trackSearch,
        trackCTAClick: trackCTAClick,

        // Eventos de erro
        trackError: trackError,

        // Helpers
        sendEvent: sendEvent,
        isGtagAvailable: isGtagAvailable,
    };
})();

// Auto-inicializa quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa com todas as funcionalidades
    GeekAnalytics.init({
        debug: window.location.hostname === 'localhost',
        scroll: true,
        errors: true,
        affiliates: true,
        share: true,
    });
});
