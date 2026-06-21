"""
Calculo das metricas do dashboard.

Indicadores:
- product_clicks: cliques em produtos (afiliado) nas ultimas 24h, com trend
  vs as 24h anteriores.
- new_products: produtos cadastrados nos ultimos 7 dias, com trend vs os 7
  dias anteriores.
- last_product: nome do ultimo produto cadastrado e ha quanto tempo.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.click import ClickRepository
from app.repositories.product import ProductRepository


def _trend(current: int, previous: int) -> dict:
    """Monta o bloco de tendencia entre o periodo atual e o anterior."""
    if previous == 0:
        # Sem base de comparacao: nao da pra calcular %.
        trend_pct = None
    else:
        trend_pct = round((current - previous) / previous * 100, 1)

    if current > previous:
        direction = "up"
    elif current < previous:
        direction = "down"
    else:
        direction = "flat"

    return {
        "current": current,
        "previous": previous,
        "trend_pct": trend_pct,
        "direction": direction,
    }


def _ago(created_at: datetime, now: datetime) -> dict:
    """Calcula ha quanto tempo (min/horas/dias) a partir de created_at."""
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)

    total_minutes = max(0, int((now - created_at).total_seconds() // 60))

    if total_minutes < 60:
        text = f"{total_minutes} min"
    elif total_minutes < 1440:
        text = f"{total_minutes // 60} h"
    else:
        text = f"{total_minutes // 1440} d"

    return {"minutes": total_minutes, "text": text}


async def get_dashboard_metrics(db: AsyncSession) -> dict:
    """Calcula e retorna todas as metricas do dashboard."""
    now = datetime.now(UTC)
    click_repo = ClickRepository(db)
    product_repo = ProductRepository(db)

    # --- Cliques em produtos: ultimas 24h vs as 24h anteriores ---
    h24 = now - timedelta(hours=24)
    h48 = now - timedelta(hours=48)
    product_clicks_current = await click_repo.count_in_period(h24, now)
    product_clicks_previous = await click_repo.count_in_period(h48, h24)

    # --- Novos produtos: ultimos 7 dias vs os 7 dias anteriores ---
    d7 = now - timedelta(days=7)
    d14 = now - timedelta(days=14)
    products_current = await product_repo.count_created_in_period(d7, now)
    products_previous = await product_repo.count_created_in_period(d14, d7)

    # --- Ultimo produto cadastrado ---
    last_product = await product_repo.get_last_created()
    last_product_data = None
    if last_product is not None:
        last_product_data = {
            "name": last_product.name,
            "slug": last_product.slug,
            "created_at": last_product.created_at.isoformat(),
            "ago": _ago(last_product.created_at, now),
        }

    return {
        "generated_at": now.isoformat(),
        "product_clicks_24h": {
            "label": "Cliques em produtos (24h)",
            "source": "affiliate_clicks",
            **_trend(product_clicks_current, product_clicks_previous),
        },
        "new_products_7d": {
            "label": "Novos produtos (7 dias)",
            **_trend(products_current, products_previous),
        },
        "last_product": last_product_data,
    }
