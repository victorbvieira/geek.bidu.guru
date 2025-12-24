"""
Servico de protecao anti-spam para formularios publicos.

Implementa multiplas camadas de protecao:
1. Honeypot: Campo invisivel que bots preenchem
2. Rate Limiting por IP: Limita requisicoes por IP
3. Rate Limiting por Email: Limita tentativas por email
4. Tempo minimo de preenchimento: Bots sao muito rapidos
5. Blocklist de dominios descartaveis
6. Validacao de User-Agent

Referencia de mercado:
- Mailchimp, ConvertKit, Sendinblue usam tecnicas similares
- reCAPTCHA e hCaptcha sao alternativas mais invasivas
"""

import hashlib
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request, status

from app.config import settings

logger = logging.getLogger(__name__)


# Cache em memoria para rate limiting (em producao, usar Redis)
# Estrutura: {"ip_hash": {"count": int, "first_request": timestamp}}
_rate_limit_cache: dict[str, dict] = {}

# Cache para emails (limita reenvios de verificacao)
_email_rate_cache: dict[str, dict] = {}


# =============================================================================
# Configuracoes Anti-Spam
# =============================================================================

# Rate limiting por IP
RATE_LIMIT_IP_MAX_REQUESTS = 10  # Max requisicoes
RATE_LIMIT_IP_WINDOW_SECONDS = 3600  # Janela de 1 hora

# Rate limiting por email (reenvio de verificacao)
RATE_LIMIT_EMAIL_MAX_REQUESTS = 3  # Max 3 tentativas por email
RATE_LIMIT_EMAIL_WINDOW_SECONDS = 3600  # Por hora

# Tempo minimo de preenchimento do formulario (em segundos)
MIN_FORM_FILL_TIME_SECONDS = 2

# Lista de dominios de email descartavel/temporario (atualize conforme necessario)
DISPOSABLE_EMAIL_DOMAINS = {
    # Servicos mais conhecidos de email temporario
    "10minutemail.com",
    "10minutemail.net",
    "guerrillamail.com",
    "guerrillamail.org",
    "guerrillamail.net",
    "mailinator.com",
    "maildrop.cc",
    "tempmail.com",
    "temp-mail.org",
    "throwaway.email",
    "fakeinbox.com",
    "sharklasers.com",
    "yopmail.com",
    "yopmail.fr",
    "trashmail.com",
    "mailnesia.com",
    "mailcatch.com",
    "mintemail.com",
    "dispostable.com",
    "tempr.email",
    "tempail.com",
    "mohmal.com",
    "getnada.com",
    "emailondeck.com",
    "spamgourmet.com",
    "mytrashmail.com",
    "getairmail.com",
    "discard.email",
    "discardmail.com",
    "spambog.com",
    "spambog.de",
    "spambog.ru",
    "mailexpire.com",
    "tempinbox.com",
    "fakemailgenerator.com",
    "emailfake.com",
    "crazymailing.com",
    "tempsky.com",
}


# =============================================================================
# Funcoes de Validacao
# =============================================================================


def _hash_ip(ip: str) -> str:
    """Cria hash do IP para privacidade."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def _get_client_ip(request: Request) -> str:
    """
    Extrai IP do cliente considerando proxies.

    Ordem de prioridade:
    1. X-Forwarded-For (primeiro IP da lista)
    2. X-Real-IP
    3. client.host
    """
    # X-Forwarded-For pode ter multiplos IPs: "client, proxy1, proxy2"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


def _clean_expired_cache() -> None:
    """Remove entradas expiradas dos caches."""
    now = time.time()

    # Limpa cache de IP
    expired_ips = [
        key
        for key, value in _rate_limit_cache.items()
        if now - value.get("first_request", 0) > RATE_LIMIT_IP_WINDOW_SECONDS
    ]
    for key in expired_ips:
        del _rate_limit_cache[key]

    # Limpa cache de email
    expired_emails = [
        key
        for key, value in _email_rate_cache.items()
        if now - value.get("first_request", 0) > RATE_LIMIT_EMAIL_WINDOW_SECONDS
    ]
    for key in expired_emails:
        del _email_rate_cache[key]


def check_rate_limit_ip(request: Request) -> None:
    """
    Verifica rate limit por IP.

    Raises:
        HTTPException 429: Se limite excedido
    """
    _clean_expired_cache()

    client_ip = _get_client_ip(request)
    ip_hash = _hash_ip(client_ip)
    now = time.time()

    if ip_hash in _rate_limit_cache:
        cache = _rate_limit_cache[ip_hash]

        # Verifica se janela expirou
        if now - cache["first_request"] > RATE_LIMIT_IP_WINDOW_SECONDS:
            _rate_limit_cache[ip_hash] = {"count": 1, "first_request": now}
        else:
            cache["count"] += 1

            if cache["count"] > RATE_LIMIT_IP_MAX_REQUESTS:
                logger.warning(
                    "Rate limit excedido para IP: %s (hash: %s)",
                    client_ip,
                    ip_hash,
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Muitas tentativas. Aguarde alguns minutos.",
                )
    else:
        _rate_limit_cache[ip_hash] = {"count": 1, "first_request": now}


def check_rate_limit_email(email: str) -> None:
    """
    Verifica rate limit por email.

    Evita que o mesmo email receba muitos emails de verificacao.

    Raises:
        HTTPException 429: Se limite excedido
    """
    _clean_expired_cache()

    email_lower = email.lower()
    now = time.time()

    if email_lower in _email_rate_cache:
        cache = _email_rate_cache[email_lower]

        if now - cache["first_request"] > RATE_LIMIT_EMAIL_WINDOW_SECONDS:
            _email_rate_cache[email_lower] = {"count": 1, "first_request": now}
        else:
            cache["count"] += 1

            if cache["count"] > RATE_LIMIT_EMAIL_MAX_REQUESTS:
                logger.warning("Rate limit de email excedido para: %s", email_lower)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Email de verificacao ja enviado. Verifique sua caixa de entrada ou aguarde.",
                )
    else:
        _email_rate_cache[email_lower] = {"count": 1, "first_request": now}


def check_honeypot(honeypot_value: Optional[str]) -> None:
    """
    Verifica campo honeypot.

    O honeypot e um campo invisivel no formulario. Usuarios reais
    nao o preenchem, mas bots automaticos sim.

    Args:
        honeypot_value: Valor do campo honeypot (deve ser vazio ou None)

    Raises:
        HTTPException 400: Se honeypot preenchido (indica bot)
    """
    if honeypot_value:
        logger.warning("Honeypot detectado! Valor: %s", honeypot_value[:50])
        # Retorna erro generico para nao dar dicas ao bot
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao processar formulario.",
        )


def check_min_fill_time(timestamp_value: Optional[str]) -> None:
    """
    Verifica tempo minimo de preenchimento do formulario.

    Bots preenchem formularios instantaneamente. Usuarios reais
    levam alguns segundos.

    Args:
        timestamp_value: Timestamp (em segundos) de quando o form foi carregado

    Raises:
        HTTPException 400: Se formulario preenchido muito rapido
    """
    if not timestamp_value:
        # Se nao tiver timestamp, ignora verificacao (compatibilidade)
        return

    try:
        form_loaded_at = float(timestamp_value)
        now = time.time()
        fill_time = now - form_loaded_at

        if fill_time < MIN_FORM_FILL_TIME_SECONDS:
            logger.warning(
                "Formulario preenchido muito rapido: %.2f segundos",
                fill_time,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao processar formulario.",
            )
    except (ValueError, TypeError):
        # Timestamp invalido - ignora
        pass


def check_disposable_email(email: str) -> None:
    """
    Verifica se email e de dominio descartavel/temporario.

    Emails temporarios sao frequentemente usados por spammers
    e nao convertem em usuarios reais.

    Args:
        email: Email a verificar

    Raises:
        HTTPException 400: Se dominio for descartavel
    """
    domain = email.lower().split("@")[-1]

    if domain in DISPOSABLE_EMAIL_DOMAINS:
        logger.warning("Tentativa de uso de email descartavel: %s", domain)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Por favor, use um email permanente.",
        )


def check_user_agent(request: Request) -> None:
    """
    Verifica User-Agent basico.

    Bots simples frequentemente nao enviam User-Agent ou usam
    valores suspeitos.

    Raises:
        HTTPException 400: Se User-Agent ausente ou suspeito
    """
    user_agent = request.headers.get("user-agent", "")

    # Sem User-Agent e suspeito
    if not user_agent:
        logger.warning("Requisicao sem User-Agent")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao processar formulario.",
        )

    # User-Agents muito curtos sao suspeitos
    if len(user_agent) < 10:
        logger.warning("User-Agent muito curto: %s", user_agent)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao processar formulario.",
        )

    # Bloqueia alguns bots conhecidos (adicione conforme necessario)
    suspicious_agents = [
        "curl",
        "wget",
        "python-requests",
        "scrapy",
        "httpclient",
        "java/",
        "libwww",
    ]

    user_agent_lower = user_agent.lower()
    for agent in suspicious_agents:
        if agent in user_agent_lower:
            # Em dev, permite para facilitar testes
            if settings.is_development:
                logger.debug("User-Agent suspeito permitido em dev: %s", user_agent)
                return

            logger.warning("User-Agent suspeito bloqueado: %s", user_agent)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao processar formulario.",
            )


async def validate_newsletter_submission(
    request: Request,
    email: str,
    honeypot: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> None:
    """
    Executa todas as validacoes anti-spam para inscricao na newsletter.

    Ordem das validacoes (da mais leve para mais pesada):
    1. User-Agent (rapida)
    2. Honeypot (rapida)
    3. Tempo minimo (rapida)
    4. Rate limit IP (cache lookup)
    5. Rate limit email (cache lookup)
    6. Email descartavel (string comparison)

    Args:
        request: Request do FastAPI
        email: Email sendo cadastrado
        honeypot: Valor do campo honeypot (deve ser vazio)
        timestamp: Timestamp de quando o form foi carregado

    Raises:
        HTTPException: Se qualquer validacao falhar
    """
    # 1. Verifica User-Agent
    check_user_agent(request)

    # 2. Verifica honeypot (campo invisivel)
    check_honeypot(honeypot)

    # 3. Verifica tempo minimo de preenchimento
    check_min_fill_time(timestamp)

    # 4. Rate limit por IP
    check_rate_limit_ip(request)

    # 5. Rate limit por email
    check_rate_limit_email(email)

    # 6. Verifica email descartavel
    check_disposable_email(email)

    logger.debug("Validacao anti-spam passou para email: %s", email)
