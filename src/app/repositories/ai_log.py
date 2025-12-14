"""
Repositorio para logs de chamadas LLM.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_log import AILog


class AILogRepository:
    """Repositorio para operacoes de AILog."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        use_case: str,
        provider: str,
        model: str,
        user_prompt: str,
        *,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_content: str | None = None,
        finish_reason: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_tokens: int | None = None,
        cost_usd: Decimal | None = None,
        latency_ms: int | None = None,
        success: bool = True,
        error_message: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> AILog:
        """
        Cria um novo registro de log.

        Args:
            use_case: Caso de uso (post_tags, seo_title, etc)
            provider: Provider (openai, openrouter, etc)
            model: Modelo usado
            user_prompt: User prompt enviado
            entity_type: Tipo da entidade (post, category, etc)
            entity_id: ID da entidade relacionada
            system_prompt: System prompt enviado
            temperature: Temperature configurado
            max_tokens: Max tokens configurado
            response_content: Conteudo da resposta
            finish_reason: Razao de finalizacao
            prompt_tokens: Tokens de entrada
            completion_tokens: Tokens de saida
            total_tokens: Total de tokens
            cost_usd: Custo em USD
            latency_ms: Latencia em milissegundos
            success: Se a chamada foi bem sucedida
            error_message: Mensagem de erro se falhou
            user_id: ID do usuario admin

        Returns:
            AILog criado
        """
        log = AILog(
            use_case=use_case,
            provider=provider,
            model=model,
            user_prompt=user_prompt,
            entity_type=entity_type,
            entity_id=entity_id,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_content=response_content,
            finish_reason=finish_reason,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message,
            user_id=user_id,
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        use_case: str | None = None,
        success: bool | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
    ) -> list[AILog]:
        """
        Lista logs com filtros opcionais.

        Args:
            limit: Maximo de registros
            offset: Pular N registros
            use_case: Filtrar por caso de uso
            success: Filtrar por sucesso/erro
            entity_type: Filtrar por tipo de entidade
            entity_id: Filtrar por ID de entidade

        Returns:
            Lista de AILog
        """
        query = select(AILog).order_by(desc(AILog.created_at))

        if use_case:
            query = query.where(AILog.use_case == use_case)
        if success is not None:
            query = query.where(AILog.success == success)
        if entity_type:
            query = query.where(AILog.entity_type == entity_type)
        if entity_id:
            query = query.where(AILog.entity_id == entity_id)

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get(self, log_id: uuid.UUID) -> AILog | None:
        """Busca log por ID."""
        result = await self.db.execute(
            select(AILog).where(AILog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def count(
        self,
        use_case: str | None = None,
        success: bool | None = None,
    ) -> int:
        """Conta logs com filtros opcionais."""
        from sqlalchemy import func
        query = select(func.count(AILog.id))

        if use_case:
            query = query.where(AILog.use_case == use_case)
        if success is not None:
            query = query.where(AILog.success == success)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_total_cost(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> Decimal:
        """Calcula custo total no periodo."""
        from sqlalchemy import func
        query = select(func.sum(AILog.cost_usd)).where(AILog.success == True)

        if start_date:
            query = query.where(AILog.created_at >= start_date)
        if end_date:
            query = query.where(AILog.created_at <= end_date)

        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")
