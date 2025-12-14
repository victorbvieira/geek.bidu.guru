"""
Modulo de seguranca - hashing de senhas e tokens JWT.

Implementa:
- Hashing de senhas com bcrypt
- Geracao e validacao de tokens JWT (access e refresh)
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# -----------------------------------------------------------------------------
# Password Hashing
# -----------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha plain corresponde ao hash.

    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash bcrypt da senha

    Returns:
        True se a senha estiver correta, False caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera hash bcrypt da senha.

    Args:
        password: Senha em texto plano

    Returns:
        Hash bcrypt da senha
    """
    return pwd_context.hash(password)


# -----------------------------------------------------------------------------
# JWT Tokens
# -----------------------------------------------------------------------------


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Cria token JWT de acesso.

    Args:
        subject: Identificador do usuario (geralmente user_id ou email)
        expires_delta: Tempo de expiracao customizado
        extra_claims: Claims adicionais para incluir no token

    Returns:
        Token JWT assinado
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
        "iat": datetime.now(UTC),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Cria token JWT de refresh (renovacao).

    Args:
        subject: Identificador do usuario
        expires_delta: Tempo de expiracao customizado

    Returns:
        Token JWT de refresh assinado
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(UTC),
    }

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_token(token: str, token_type: str = "access") -> dict[str, Any] | None:
    """
    Verifica e decodifica um token JWT.

    Args:
        token: Token JWT a ser verificado
        token_type: Tipo esperado do token ("access" ou "refresh")

    Returns:
        Payload do token se valido, None caso contrario
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        # Verificar tipo do token
        if payload.get("type") != token_type:
            return None

        # Verificar se tem subject
        if payload.get("sub") is None:
            return None

        return payload

    except JWTError:
        return None


def should_renew_token(payload: dict[str, Any], threshold_percent: float = 0.5) -> bool:
    """
    Verifica se o token deve ser renovado (sliding expiration).

    Renova quando o tempo restante for menor que o percentual definido
    do tempo total de vida do token.

    Por exemplo, com threshold_percent=0.5 e token de 120 minutos:
    - Token criado agora: 120 min restantes -> NAO renova
    - Token com 60 min restantes (50%): -> RENOVA
    - Token com 30 min restantes: -> RENOVA

    Args:
        payload: Payload do token JWT decodificado
        threshold_percent: Percentual do tempo de vida para trigger de renovacao
                          (padrao: 0.5 = 50% do tempo restante)

    Returns:
        True se o token deve ser renovado, False caso contrario
    """
    try:
        # Obter timestamps do token
        exp_timestamp = payload.get("exp")
        iat_timestamp = payload.get("iat")

        if not exp_timestamp or not iat_timestamp:
            return False

        now = datetime.now(UTC)
        exp_time = datetime.fromtimestamp(exp_timestamp, tz=UTC)
        iat_time = datetime.fromtimestamp(iat_timestamp, tz=UTC)

        # Calcular tempo total de vida e tempo restante
        total_lifetime = (exp_time - iat_time).total_seconds()
        remaining_time = (exp_time - now).total_seconds()

        # Se o tempo restante for menor que o threshold, renovar
        threshold_seconds = total_lifetime * threshold_percent

        return remaining_time < threshold_seconds

    except (TypeError, ValueError):
        return False
