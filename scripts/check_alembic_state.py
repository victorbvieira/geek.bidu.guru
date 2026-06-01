"""Sanity check do estado do alembic_version antes do upgrade.

Roda automaticamente no entrypoint do container (ver `docker/Dockerfile`),
ANTES de `alembic upgrade head`. Falha rápido com mensagem clara se a
tabela `alembic_version` estiver em estado inconsistente:

- Mais de uma linha → loop de migration (foi o que aconteceu no incidente
  de 2026-06-01 após restore de backup antigo).
- Linha com revision que não existe nos arquivos → upgrade nunca completa.

Em ambos os casos, melhor abortar e exigir intervenção humana do que
deixar o container reiniciando indefinidamente (e o resto da app fora do ar).

Como usar:
    python -m scripts.check_alembic_state

Exit codes:
    0 — tudo OK, pode rodar `alembic upgrade head`
    1 — estado inconsistente, NÃO rodar upgrade
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Sem dependências externas além de psycopg2 (já presente em requirements)
import psycopg2


def known_revisions() -> set[str]:
    """Lê as revisions disponíveis nos arquivos de migration."""
    versions_dir = Path(__file__).resolve().parents[1] / "src" / "migrations" / "versions"
    revs: set[str] = set()
    for f in versions_dir.glob("*.py"):
        if f.name.startswith("__"):
            continue
        for line in f.read_text().splitlines():
            line = line.strip()
            if line.startswith("revision: str = "):
                # revision: str = "001"
                token = line.split("=", 1)[1].strip().strip("\"'")
                revs.add(token)
                break
    return revs


def database_url() -> str:
    """Lê DATABASE_URL do env. Aborta se ausente."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("FATAL: DATABASE_URL não definida no env")
    # Normaliza driver async → sync (psycopg2 não entende +asyncpg)
    return url.replace("postgresql+asyncpg://", "postgresql://").replace(
        "postgres+asyncpg://", "postgres://"
    )


def connect(url: str):
    """Abre conexão psycopg2."""
    parsed = urlparse(url)
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        dbname=(parsed.path or "/").lstrip("/"),
    )


def main() -> int:
    url = database_url()
    revs = known_revisions()
    print(f"[check-alembic] {len(revs)} revisions encontradas no código: {sorted(revs)}")

    try:
        conn = connect(url)
    except Exception as e:
        print(f"[check-alembic] Não conectou no banco: {e}")
        print("[check-alembic] Pode ser primeiro boot — deixando alembic criar tudo")
        return 0

    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT EXISTS ("
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'alembic_version'"
            ")"
        )
        exists = cur.fetchone()[0]
        if not exists:
            print("[check-alembic] Tabela alembic_version não existe — banco vazio, OK.")
            return 0

        cur.execute("SELECT version_num FROM alembic_version ORDER BY version_num")
        rows = [r[0] for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

    if len(rows) == 0:
        print("[check-alembic] alembic_version está vazia — OK, alembic vai stampear.")
        return 0

    if len(rows) > 1:
        print(
            f"[check-alembic] FATAL: alembic_version tem {len(rows)} linhas: {rows}\n"
            "Deve ter exatamente UMA. Investigue (possível restore de backup antigo).\n"
            "Para corrigir:\n"
            "  DELETE FROM alembic_version WHERE version_num NOT IN ('<correta>');\n"
            "Depois reinicie o container."
        )
        return 1

    current = rows[0]
    if current not in revs:
        print(
            f"[check-alembic] FATAL: alembic_version = {current!r} não existe nos arquivos.\n"
            f"Revisions disponíveis: {sorted(revs)}\n"
            "Possíveis causas:\n"
            "  - Banco está em revision antiga que foi removida no squash\n"
            "  - Restore de backup com formato de ID diferente (ex: '0015' vs '015')\n"
            "Para corrigir (se sabe a equivalência):\n"
            "  UPDATE alembic_version SET version_num = '<revision-equivalente>';\n"
            "Depois reinicie o container."
        )
        return 1

    print(f"[check-alembic] OK — alembic_version = {current!r}, conhecida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
