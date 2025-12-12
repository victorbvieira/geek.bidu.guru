"""
Middlewares de seguranca para a aplicacao.

Implementa headers de seguranca conforme OWASP.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adiciona headers de seguranca a todas as respostas.

    Headers implementados:
    - X-Content-Type-Options: Previne MIME sniffing
    - X-Frame-Options: Previne clickjacking
    - X-XSS-Protection: Proteção XSS (legacy browsers)
    - Strict-Transport-Security: Força HTTPS
    - Referrer-Policy: Controla informacao de referrer
    - Permissions-Policy: Restringe APIs do navegador
    - Content-Security-Policy: Controla fontes de conteudo
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Previne MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Previne clickjacking (pagina nao pode ser embedada em iframe)
        response.headers["X-Frame-Options"] = "DENY"

        # Proteção XSS para browsers antigos
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Força HTTPS (1 ano, incluindo subdomínios)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Controla informacao enviada no header Referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restringe APIs do navegador que nao usamos
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )

        # Content Security Policy
        # Configuracao mais restritiva para producao
        if settings.is_production:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "img-src 'self' data: https: blob:",
                "font-src 'self' https://fonts.gstatic.com",
                "connect-src 'self' https://www.google-analytics.com https://region1.google-analytics.com",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
        else:
            # Em desenvolvimento, mais permissivo para facilitar debug
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https: blob:",
                "font-src 'self' data:",
                "connect-src 'self' ws: wss:",
            ]

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        return response
