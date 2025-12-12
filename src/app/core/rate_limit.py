"""
Rate Limiting com SlowAPI.

Protege endpoints contra abuso e ataques de força bruta.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter global usando IP como chave
limiter = Limiter(key_func=get_remote_address)


# Constantes de limite
RATE_LIMIT_DEFAULT = "100/minute"
RATE_LIMIT_AUTH = "5/minute"
RATE_LIMIT_SEARCH = "30/minute"
RATE_LIMIT_CONTACT = "3/hour"
RATE_LIMIT_NEWSLETTER = "5/hour"
