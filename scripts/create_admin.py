#!/usr/bin/env python3
"""
Script para criar usuário admin no banco de dados.
Útil para primeiro deploy ou reset de senha.

Uso:
    python scripts/create_admin.py

Ou dentro do container:
    docker exec -it geek_app python /app/scripts/create_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.database import AsyncSessionLocal
from app.models.admin import Admin
from app.core.security import hash_password


async def create_admin():
    """Cria um usuário admin no banco de dados."""
    print("=" * 60)
    print("Criação de Usuário Administrador - geek.bidu.guru")
    print("=" * 60)
    print()

    # Solicitar dados do admin
    username = input("Username (ex: admin): ").strip()
    if not username:
        print("❌ Username é obrigatório!")
        return

    email = input("Email (ex: admin@exemplo.com): ").strip()
    if not email:
        print("❌ Email é obrigatório!")
        return

    password = input("Senha (mínimo 8 caracteres): ").strip()
    if not password or len(password) < 8:
        print("❌ Senha deve ter pelo menos 8 caracteres!")
        return

    password_confirm = input("Confirme a senha: ").strip()
    if password != password_confirm:
        print("❌ Senhas não coincidem!")
        return

    print()
    print("Criando usuário admin...")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print()

    try:
        async with AsyncSessionLocal() as db:
            # Verificar se username já existe
            from sqlalchemy import select

            stmt = select(Admin).where(Admin.username == username)
            result = await db.execute(stmt)
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print(f"⚠️  Admin '{username}' já existe!")
                update = input("Deseja atualizar a senha? (s/N): ").strip().lower()
                if update == "s":
                    existing_admin.hashed_password = hash_password(password)
                    existing_admin.email = email
                    existing_admin.is_active = True
                    await db.commit()
                    print(f"✅ Senha do admin '{username}' atualizada com sucesso!")
                else:
                    print("❌ Operação cancelada.")
                return

            # Criar novo admin
            admin = Admin(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                is_active=True,
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)

            print()
            print("=" * 60)
            print("✅ Admin criado com sucesso!")
            print("=" * 60)
            print(f"ID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Ativo: {admin.is_active}")
            print(f"Criado em: {admin.created_at}")
            print()
            print("Você pode fazer login em:")
            print("  https://geek.bidu.guru/admin/login")
            print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Erro ao criar admin!")
        print("=" * 60)
        print(f"Erro: {e}")
        print()
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(create_admin())
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
        sys.exit(1)
