/**
 * main.js - geek.bidu.guru
 * JavaScript principal da aplicacao
 */

// =============================================================================
// Mobile Menu Toggle
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', () => {
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isExpanded);
            mainNav.classList.toggle('is-open');
        });
    }
});

// =============================================================================
// Newsletter Form
// =============================================================================
// NOTA: O handler do formulario de newsletter foi movido para templates/home.html
// onde ha uma implementacao completa com AJAX e modal animado.
// Este bloco foi removido para evitar conflito de event listeners.

// =============================================================================
// Smooth Scroll para links internos
// =============================================================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// =============================================================================
// Analytics Events (placeholder para GA4)
// =============================================================================
const trackEvent = (eventName, params = {}) => {
    // TODO: Implementar GA4
    console.log('Track Event:', eventName, params);

    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, params);
    }
};

// Exemplo: Track cliques em links de afiliados
document.querySelectorAll('a[href*="/goto/"]').forEach(link => {
    link.addEventListener('click', () => {
        trackEvent('affiliate_click', {
            destination: link.href,
            product_name: link.dataset.productName || 'unknown'
        });
    });
});
