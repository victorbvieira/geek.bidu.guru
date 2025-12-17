"""
Middlewares de seguranca para a aplicacao.

Implementa headers de seguranca conforme OWASP.
Implementa sliding expiration para tokens JWT do admin.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings
from app.core.security import create_access_token, should_renew_token, verify_token


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
        # Permite que endpoints específicos definam seu próprio X-Frame-Options
        # (ex: previews que precisam ser carregados em iframes do mesmo domínio)
        if "X-Frame-Options" not in response.headers:
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


class AdminTokenRenewalMiddleware(BaseHTTPMiddleware):
    """
    Middleware para renovacao automatica do token JWT do admin (sliding expiration).

    Quando o usuario esta ativo no painel admin e o token esta proximo de expirar
    (menos de 50% do tempo restante), o middleware gera um novo token automaticamente
    e atualiza o cookie.

    Isso garante que usuarios ativos nunca sejam deslogados enquanto estiverem
    usando o sistema.

    Exemplo com token de 120 minutos:
    - 0-60 min de uso: token original mantido
    - 60+ min de uso: novo token gerado (mais 120 min)
    - Usuario ativo indefinidamente: sessao nunca expira

    Importante:
    - Aplica apenas a rotas /admin/*
    - Ignora rotas de login/logout
    - Requer que o token atual seja valido
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Aplica apenas a rotas do admin (exceto login/logout)
        path = request.url.path
        if not path.startswith("/admin"):
            return response

        # Ignorar rotas de autenticacao
        if path in ["/admin/login", "/admin/logout"]:
            return response

        # Verificar se tem token no cookie
        token = request.cookies.get("admin_token")
        if not token:
            return response

        # Verificar se o token e valido
        payload = verify_token(token, token_type="access")
        if not payload:
            return response

        # Verificar se precisa renovar (menos de 50% do tempo restante)
        if not should_renew_token(payload, threshold_percent=0.5):
            return response

        # Renovar o token
        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id:
            return response

        # Criar novo token com os mesmos claims
        extra_claims = {"role": role} if role else None
        new_token = create_access_token(subject=user_id, extra_claims=extra_claims)

        # Configuracao do cookie baseada no ambiente
        is_production = settings.environment == "production"
        cookie_max_age = settings.jwt_access_token_expire_minutes * 60

        # Atualizar o cookie com o novo token
        response.set_cookie(
            key="admin_token",
            value=new_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=cookie_max_age,
        )

        return response
