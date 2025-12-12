"""
Testes unitarios para headers de seguranca.

Verifica que os headers OWASP estao sendo aplicados.
"""

import pytest


class TestSecurityHeaders:
    """Testes para headers de seguranca."""

    @pytest.mark.asyncio
    async def test_x_content_type_options(self, client):
        """Header X-Content-Type-Options deve ser nosniff."""
        response = await client.get("/")

        assert response.headers.get("x-content-type-options") == "nosniff"

    @pytest.mark.asyncio
    async def test_x_frame_options(self, client):
        """Header X-Frame-Options deve ser DENY."""
        response = await client.get("/")

        assert response.headers.get("x-frame-options") == "DENY"

    @pytest.mark.asyncio
    async def test_x_xss_protection(self, client):
        """Header X-XSS-Protection deve estar presente."""
        response = await client.get("/")

        assert response.headers.get("x-xss-protection") == "1; mode=block"

    @pytest.mark.asyncio
    async def test_referrer_policy(self, client):
        """Header Referrer-Policy deve estar configurado."""
        response = await client.get("/")

        assert (
            response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
        )

    @pytest.mark.asyncio
    async def test_permissions_policy(self, client):
        """Header Permissions-Policy deve restringir APIs."""
        response = await client.get("/")

        permissions = response.headers.get("permissions-policy")
        assert permissions is not None
        assert "camera=()" in permissions
        assert "microphone=()" in permissions
        assert "geolocation=()" in permissions

    @pytest.mark.asyncio
    async def test_content_security_policy(self, client):
        """Header Content-Security-Policy deve estar presente."""
        response = await client.get("/")

        csp = response.headers.get("content-security-policy")
        assert csp is not None
        assert "default-src" in csp

    @pytest.mark.asyncio
    async def test_security_headers_on_api(self, client):
        """Headers de seguranca devem estar presentes em rotas API."""
        response = await client.get("/health")

        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"

    @pytest.mark.asyncio
    async def test_security_headers_on_static(self, client):
        """Headers de seguranca devem estar presentes em arquivos estaticos."""
        response = await client.get("/static/css/main.css")

        # Mesmo em 404, headers devem estar presentes
        assert response.headers.get("x-content-type-options") == "nosniff"
