# Squash de migrations — 2026-06-01

> Documento de referência sobre o squash que consolidou 40 migrations
> antigas em 2 migrations (`001_consolidated_schema` + `002_consolidated_seeds`).

## Por que

1. **41 migrations acumuladas** desde 2025-12-11 com 3 estilos de ID mistos
   (3-dígitos: `001`, `015`; 3-dígitos+letra: `008a`, `024c`; hash: `7d02c38a81cd`)
   — confuso para devs novos e para `alembic history`.
2. **Incidente de produção em 2026-06-01**: restore de backup antigo trouxe
   `alembic_version = '0015'` (formato 4-dígitos não usado mais), causou
   loop infinito de boot por incompatibilidade com IDs atuais (`015`). Fix
   imediato foi `DELETE FROM alembic_version WHERE version_num = '0015'`.
3. **Sistema está estável** em produção, momento certo pra resetar a base
   antes que acumule mais 40 migrations.

## O que mudou

### Arquivos em `src/migrations/versions/`

**Antes:** 41 arquivos (~3000 linhas, mistura de formatos)
**Depois:** 2 arquivos
- `20260101_001_consolidated_schema.py` — DDL completo via `Base.metadata.create_all` + triggers + GIN indexes
- `20260101_002_consolidated_seeds.py` — admin user + automation user + ai_configs essenciais

### Novo check defensivo

- `scripts/check_alembic_state.py` — roda ANTES de `alembic upgrade head`
  no entrypoint do Docker. Aborta cedo com mensagem clara se:
  - `alembic_version` tem mais de 1 linha
  - revision atual no banco não existe nos arquivos

Previne reincidência do incidente de 2026-06-01.

### Dockerfile

CMD passou de:
```
alembic upgrade head && uvicorn ...
```
para:
```
python scripts/check_alembic_state.py && alembic upgrade head && uvicorn ...
```

## Como migrar ambientes

### Fresh install (banco vazio)

Normal: `alembic upgrade head` aplica `001` e `002`. Pronto em segundos.

### Banco legado em revision `029` ou posterior (produção)

**IMPORTANTE: NÃO rode `alembic upgrade head` direto** — vai tentar criar
tabelas que já existem e falhar.

Em vez disso, faça stamping manual:

```sql
-- Conecte no Postgres do ambiente
DELETE FROM alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('002');
```

Isso marca o banco como "já em 002" sem rodar nada. O check defensivo no
próximo boot vai validar e prosseguir.

### Banco legado em revision desconhecida

O check defensivo no entrypoint vai abortar com mensagem clara incluindo
as revisions disponíveis. Identifique manualmente o estado e:

- Se o schema corresponde ao que `001+002` produzem: stamp para `002`
- Se está atrasado: dump dos dados, drop tudo, fresh install, restore só
  dos dados (não da metadata do alembic)

## Como verificar se um ambiente está OK

```bash
docker exec -it <container> python scripts/check_alembic_state.py
```

Deve imprimir algo como:
```
[check-alembic] 2 revisions encontradas no código: ['001', '002']
[check-alembic] OK — alembic_version = '002', conhecida.
```

## Como evolver daqui

Próximas migrations seguem o fluxo normal: `alembic revision --autogenerate -m "msg"`
gera ID hash (ou use 3-dígitos manualmente: `003`, `004`...). Encadeiam a
partir de `002`.

Se daqui a um ano acumular outras 40 migrations, repita esse processo de
squash. Esse documento serve de receita.

## Histórico das 40 migrations descartadas

Preservado em git: `git log --all -- src/migrations/versions/` ou em commits
anteriores a este squash. Lista resumida do que era:

- `001-005`: schema inicial (users, categorias, posts, produtos, sessions, newsletter, redirects)
- `006-011 + hashes`: ai_configs, occasions, ai_logs, user_prompts, content+next_review
- `012-014`: ocasiões + tags + ai cost
- `015-018`: fixes em occasion configs (provider, prompts, max_tokens)
- `019-021`: category ai configs, product post tracking
- `022-024`: instagram metadata + history + product ai configs
- `025-026`: social integrations + price history
- `027-028`: newsletter (verification, LGPD ip fields)
- `029`: category header image
- `030`: api_tokens
