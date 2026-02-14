#!/usr/bin/env python3
"""
Script para testar conexão com o banco de dados PostgreSQL.
Útil para debug de problemas de conexão.

Uso:
    python scripts/test_database.py

Ou dentro do container:
    docker exec -it geek_app python /app/scripts/test_database.py
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def test_database():
    """Testa a conexão com o banco de dados."""
    print("=" * 60)
    print("Teste de Conexão com PostgreSQL - geek.bidu.guru")
    print("=" * 60)
    print()

    try:
        from app.config import settings

        print("📋 Configurações:")
        print(f"  Ambiente: {settings.environment}")
        print(f"  Debug: {settings.debug}")
        print(f"  App URL: {settings.app_url}")
        print()

        # Exibir DATABASE_URL ocultando senha
        db_url = str(settings.DATABASE_URL)
        # Ocultar senha na URL (postgresql://user:SENHA@host:port/db)
        import re

        db_url_safe = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", db_url)
        print(f"  Database URL: {db_url_safe}")
        print()

        print("🔌 Testando conexão com o banco de dados...")
        print()

        from app.database import check_database_connection, AsyncSessionLocal
        from sqlalchemy import text

        # Teste 1: Conexão básica
        is_connected = await check_database_connection()

        if is_connected:
            print("✅ Conexão estabelecida com sucesso!")
            print()

            # Teste 2: Executar query simples
            print("🔍 Testando query simples...")
            async with AsyncSessionLocal() as db:
                result = await db.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"  PostgreSQL Version: {version}")
                print()

                # Teste 3: Contar tabelas
                print("📊 Verificando tabelas no banco...")
                result = await db.execute(
                    text(
                        """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """
                    )
                )
                tables = result.scalars().all()

                if tables:
                    print(f"  Total de tabelas: {len(tables)}")
                    print()
                    print("  Tabelas encontradas:")
                    for table in tables:
                        print(f"    - {table}")
                    print()
                else:
                    print("  ⚠️  Nenhuma tabela encontrada!")
                    print("  Execute as migrations: alembic upgrade head")
                    print()

                # Teste 4: Verificar migrations
                print("🔄 Verificando migrations (Alembic)...")
                try:
                    result = await db.execute(
                        text("SELECT version_num FROM alembic_version")
                    )
                    version_num = result.scalar()
                    if version_num:
                        print(f"  ✅ Migration atual: {version_num}")
                    else:
                        print("  ⚠️  Nenhuma migration aplicada!")
                except Exception as e:
                    print(f"  ⚠️  Tabela alembic_version não encontrada: {e}")
                    print("  Execute: alembic upgrade head")
                print()

            print("=" * 60)
            print("✅ Todos os testes passaram!")
            print("=" * 60)
            print()

        else:
            print("=" * 60)
            print("❌ Falha ao conectar com o banco de dados!")
            print("=" * 60)
            print()
            print("Possíveis causas:")
            print("  1. DATABASE_URL incorreto")
            print("  2. PostgreSQL não está acessível")
            print("  3. Credenciais incorretas")
            print("  4. Firewall bloqueando conexão")
            print()
            sys.exit(1)

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Erro ao testar banco de dados!")
        print("=" * 60)
        print(f"Erro: {e}")
        print()
        import traceback

        traceback.print_exc()
        print()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(test_database())
    except KeyboardInterrupt:
        print("\n\n❌ Teste interrompido pelo usuário.")
        sys.exit(1)
