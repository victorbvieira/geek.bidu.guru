"""
Acesso as configuracoes da aplicacao (tabela app_settings, key/value).

Helpers simples de get/set usados pelo admin e pelas regras de negocio
(ex: tag de afiliado da Amazon).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.setting import Setting

# Chaves conhecidas
AMAZON_AFFILIATE_TAG = "amazon_affiliate_tag"


async def get_setting(
    db: AsyncSession, key: str, default: str | None = None
) -> str | None:
    """Retorna o valor de uma configuracao, ou `default` se nao existir/estiver vazia."""
    result = await db.execute(select(Setting).where(Setting.key == key))
    row = result.scalar_one_or_none()
    if row is None or row.value is None or row.value == "":
        return default
    return row.value


async def set_setting(
    db: AsyncSession,
    key: str,
    value: str | None,
    description: str | None = None,
) -> Setting:
    """Cria ou atualiza uma configuracao (get-or-create) e faz commit."""
    result = await db.execute(select(Setting).where(Setting.key == key))
    row = result.scalar_one_or_none()
    if row is None:
        row = Setting(key=key, value=value, description=description)
        db.add(row)
    else:
        row.value = value
        if description is not None:
            row.description = description
    await db.commit()
    await db.refresh(row)
    return row
