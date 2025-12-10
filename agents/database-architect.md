# Database Architect (PostgreSQL) - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: Database Architect
**Área**: Técnica / Banco de Dados
**Especialidade**: PostgreSQL, modelagem de dados, otimização de queries, índices, performance

## 🎯 Responsabilidades

- Modelagem de dados relacional
- Definição de índices e constraints
- Otimização de queries
- Migrations e versionamento de schema
- Backup e recovery
- Performance tuning
- Análise de query plans
- Definição de relacionamentos e normalização

## 🗄️ Modelagem Completa do Banco de Dados

### Diagrama ER (Entity-Relationship)

```
users (1) ----< (N) posts
categories (1) ----< (N) posts
posts (N) >----< (N) products [post_products]
posts (1) ----< (N) affiliate_clicks
products (1) ----< (N) affiliate_clicks
```

---

### 1. Tabela `users`

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'author',
        CHECK (role IN ('admin', 'editor', 'author', 'automation')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

---

### 2. Tabela `categories`

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

---

### 3. Tabela `posts`

```sql
CREATE TYPE post_type AS ENUM ('product_single', 'listicle', 'guide');
CREATE TYPE post_status AS ENUM ('draft', 'review', 'scheduled', 'published', 'archived');

CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type post_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(250) UNIQUE NOT NULL,
    subtitle VARCHAR(300),
    content TEXT NOT NULL,
    featured_image_url VARCHAR(500),

    -- SEO
    seo_focus_keyword VARCHAR(100),
    seo_title VARCHAR(60),
    seo_description VARCHAR(160),

    -- Relacionamentos
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Tags (array JSON)
    tags JSONB DEFAULT '[]'::jsonb,

    -- Status e publicação
    status post_status DEFAULT 'draft',
    publish_at TIMESTAMP,
    shared BOOLEAN DEFAULT FALSE,

    -- Métricas (desnormalizadas para performance)
    view_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_posts_slug ON posts(slug);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_type ON posts(type);
CREATE INDEX idx_posts_category ON posts(category_id);
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_publish_at ON posts(publish_at);
CREATE INDEX idx_posts_tags ON posts USING GIN(tags);
CREATE INDEX idx_posts_status_publish ON posts(status, publish_at DESC);
```

---

### 4. Tabela `products`

```sql
CREATE TYPE product_platform AS ENUM ('amazon', 'mercadolivre', 'shopee');
CREATE TYPE product_availability AS ENUM ('available', 'unavailable', 'unknown');

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(300) NOT NULL,
    slug VARCHAR(350) UNIQUE NOT NULL,

    -- Descrições
    short_description VARCHAR(500),
    long_description TEXT,

    -- Preço e moeda
    price NUMERIC(10, 2),
    currency VARCHAR(3) DEFAULT 'BRL',
    price_range VARCHAR(50),
        CHECK (price_range IN ('0-50', '50-100', '100-200', '200+')),

    -- Imagens
    main_image_url VARCHAR(500),
    images JSONB DEFAULT '[]'::jsonb,

    -- Afiliado
    affiliate_url_raw TEXT NOT NULL,
    affiliate_redirect_slug VARCHAR(150) UNIQUE NOT NULL,
    platform product_platform NOT NULL,
    platform_product_id VARCHAR(200),

    -- Categorias e Tags (JSONB)
    categories JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,

    -- Disponibilidade e avaliação
    availability product_availability DEFAULT 'unknown',
    rating NUMERIC(3, 2),
        CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER DEFAULT 0,

    -- Score interno (curadoria)
    internal_score NUMERIC(5, 2) DEFAULT 0,

    -- Atualização de preço
    last_price_update TIMESTAMP,

    -- Métricas (desnormalizadas)
    click_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_platform ON products(platform);
CREATE INDEX idx_products_availability ON products(availability);
CREATE INDEX idx_products_price_range ON products(price_range);
CREATE INDEX idx_products_internal_score ON products(internal_score DESC);
CREATE INDEX idx_products_redirect_slug ON products(affiliate_redirect_slug);
CREATE INDEX idx_products_platform_id ON products(platform, platform_product_id);
CREATE INDEX idx_products_categories ON products USING GIN(categories);
CREATE INDEX idx_products_tags ON products USING GIN(tags);
```

---

### 5. Tabela `post_products` (Relacionamento N-N)

```sql
CREATE TABLE post_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(post_id, product_id)
);

-- Índices
CREATE INDEX idx_post_products_post ON post_products(post_id);
CREATE INDEX idx_post_products_product ON post_products(product_id);
CREATE INDEX idx_post_products_position ON post_products(post_id, position);
```

---

### 6. Tabela `affiliate_clicks` (Tracking de Cliques)

```sql
CREATE TABLE affiliate_clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    post_id UUID REFERENCES posts(id) ON DELETE SET NULL,

    -- Informações da sessão
    session_id VARCHAR(100),
    user_agent TEXT,
    referer TEXT,
    ip_address VARCHAR(45),

    clicked_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_clicks_product ON affiliate_clicks(product_id);
CREATE INDEX idx_clicks_post ON affiliate_clicks(post_id);
CREATE INDEX idx_clicks_clicked_at ON affiliate_clicks(clicked_at DESC);
CREATE INDEX idx_clicks_session ON affiliate_clicks(session_id);

-- Índice composto para analytics
CREATE INDEX idx_clicks_analytics ON affiliate_clicks(product_id, clicked_at DESC);
```

---

### 7. Tabela `sessions` (Tracking de Visitantes)

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    post_id UUID REFERENCES posts(id) ON DELETE SET NULL,

    -- Informações da sessão
    user_agent TEXT,
    referer TEXT,
    ip_address VARCHAR(45),
    country VARCHAR(2),
    device_type VARCHAR(20),
        CHECK (device_type IN ('mobile', 'desktop', 'tablet', 'unknown')),

    -- Engajamento
    time_on_page INTEGER, -- segundos
    scroll_depth INTEGER, -- porcentagem (0-100)

    -- Usuário novo ou recorrente
    is_new_user BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_sessions_post ON sessions(post_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX idx_sessions_new_user ON sessions(is_new_user);
```

---

### 8. Tabela `newsletter_signups`

```sql
CREATE TABLE newsletter_signups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(200),
    session_id VARCHAR(100),
    source VARCHAR(100), -- 'homepage', 'post', 'popup'
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    unsubscribed_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_newsletter_email ON newsletter_signups(email);
CREATE INDEX idx_newsletter_active ON newsletter_signups(is_active);
CREATE INDEX idx_newsletter_subscribed_at ON newsletter_signups(subscribed_at DESC);
```

---

### 9. Tabela `ab_tests` (Testes A/B)

```sql
CREATE TABLE ab_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    hypothesis TEXT,
    variant_a_name VARCHAR(100) DEFAULT 'Control',
    variant_b_name VARCHAR(100) DEFAULT 'Treatment',
    metric VARCHAR(50), -- 'ctr', 'conversion', 'time_on_page'
    status VARCHAR(20) DEFAULT 'active',
        CHECK (status IN ('active', 'paused', 'completed')),
    start_date TIMESTAMP NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE ab_test_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID NOT NULL REFERENCES ab_tests(id) ON DELETE CASCADE,
    session_id VARCHAR(100) NOT NULL,
    variant VARCHAR(1) NOT NULL,
        CHECK (variant IN ('A', 'B')),
    event_type VARCHAR(50) NOT NULL, -- 'view', 'click', 'conversion'
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_ab_test_events_test ON ab_test_events(test_id);
CREATE INDEX idx_ab_test_events_session ON ab_test_events(session_id);
CREATE INDEX idx_ab_test_events_variant ON ab_test_events(test_id, variant);
```

## 🚀 Queries Otimizadas

### 1. Top 10 Posts Mais Vistos (Última Semana)

```sql
SELECT
    p.id,
    p.title,
    p.slug,
    COUNT(DISTINCT s.session_id) AS unique_visitors,
    COUNT(s.id) AS pageviews,
    ROUND(AVG(s.time_on_page), 0) AS avg_time_seconds,
    ROUND(AVG(s.scroll_depth), 0) AS avg_scroll_percent
FROM posts p
LEFT JOIN sessions s ON s.post_id = p.id
WHERE s.created_at >= NOW() - INTERVAL '7 days'
GROUP BY p.id, p.title, p.slug
ORDER BY unique_visitors DESC
LIMIT 10;
```

---

### 2. Produtos com Melhor Taxa de Conversão

```sql
SELECT
    pr.id,
    pr.name,
    pr.platform,
    pr.price,
    COUNT(DISTINCT s.session_id) AS total_views,
    COUNT(ac.id) AS total_clicks,
    ROUND(
        COUNT(ac.id)::NUMERIC / NULLIF(COUNT(DISTINCT s.session_id), 0) * 100,
        2
    ) AS ctr_percentage
FROM products pr
LEFT JOIN post_products pp ON pp.product_id = pr.id
LEFT JOIN sessions s ON s.post_id = pp.post_id
LEFT JOIN affiliate_clicks ac ON ac.product_id = pr.id
WHERE s.created_at >= NOW() - INTERVAL '30 days'
GROUP BY pr.id, pr.name, pr.platform, pr.price
HAVING COUNT(DISTINCT s.session_id) > 100
ORDER BY ctr_percentage DESC
LIMIT 10;
```

---

### 3. Receita Estimada por Plataforma (Mês Atual)

```sql
SELECT
    pr.platform,
    COUNT(DISTINCT pr.id) AS total_products,
    COUNT(ac.id) AS total_clicks,
    ROUND(AVG(pr.price), 2) AS avg_product_price,
    -- Estimativa de comissão (5% médio)
    ROUND(SUM(pr.price) * 0.05, 2) AS estimated_commission
FROM products pr
LEFT JOIN affiliate_clicks ac ON ac.product_id = pr.id
WHERE ac.clicked_at >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY pr.platform
ORDER BY estimated_commission DESC;
```

---

### 4. Análise de Performance por Categoria

```sql
SELECT
    c.name AS category,
    COUNT(DISTINCT p.id) AS total_posts,
    COUNT(DISTINCT s.session_id) AS total_visitors,
    ROUND(AVG(s.time_on_page), 0) AS avg_time_on_page,
    COUNT(ac.id) AS affiliate_clicks,
    ROUND(
        COUNT(ac.id)::NUMERIC / NULLIF(COUNT(DISTINCT s.session_id), 0) * 100,
        2
    ) AS ctr_percentage
FROM categories c
LEFT JOIN posts p ON p.category_id = c.id
LEFT JOIN sessions s ON s.post_id = p.id
LEFT JOIN post_products pp ON pp.post_id = p.id
LEFT JOIN affiliate_clicks ac ON ac.product_id = pp.product_id
WHERE s.created_at >= NOW() - INTERVAL '30 days'
GROUP BY c.id, c.name
ORDER BY total_visitors DESC;
```

---

### 5. Funil de Conversão de Newsletter

```sql
WITH funnel AS (
    SELECT
        DATE(s.created_at) AS date,
        COUNT(DISTINCT s.session_id) AS total_visitors,
        COUNT(DISTINCT CASE WHEN ns.id IS NOT NULL THEN s.session_id END) AS newsletter_signups
    FROM sessions s
    LEFT JOIN newsletter_signups ns ON ns.session_id = s.session_id
    WHERE s.created_at >= NOW() - INTERVAL '30 days'
    GROUP BY DATE(s.created_at)
)
SELECT
    date,
    total_visitors,
    newsletter_signups,
    ROUND(newsletter_signups::NUMERIC / NULLIF(total_visitors, 0) * 100, 2) AS conversion_rate
FROM funnel
ORDER BY date DESC;
```

## 🔧 Otimizações de Performance

### 1. VACUUM e ANALYZE

```sql
-- Rotina de manutenção (executar semanalmente)
VACUUM ANALYZE posts;
VACUUM ANALYZE products;
VACUUM ANALYZE sessions;
VACUUM ANALYZE affiliate_clicks;
```

---

### 2. Particionamento de Tabelas (Para Escala)

```sql
-- Exemplo: Particionar 'sessions' por mês
CREATE TABLE sessions (
    id UUID,
    session_id VARCHAR(100) NOT NULL,
    post_id UUID,
    created_at TIMESTAMP NOT NULL,
    -- outros campos...
) PARTITION BY RANGE (created_at);

-- Criar partições mensais
CREATE TABLE sessions_2025_01 PARTITION OF sessions
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE sessions_2025_02 PARTITION OF sessions
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Criar automaticamente com script
```

---

### 3. Índices Parciais (Para Queries Específicas)

```sql
-- Índice apenas para posts publicados
CREATE INDEX idx_posts_published
ON posts(publish_at DESC)
WHERE status = 'published';

-- Índice apenas para produtos disponíveis
CREATE INDEX idx_products_available
ON products(internal_score DESC)
WHERE availability = 'available';
```

---

### 4. Materialized Views (Para Dashboards)

```sql
-- View materializada para dashboard executivo
CREATE MATERIALIZED VIEW mv_dashboard_stats AS
SELECT
    DATE(created_at) AS date,
    COUNT(DISTINCT session_id) AS total_visitors,
    COUNT(*) AS total_pageviews,
    ROUND(AVG(time_on_page), 0) AS avg_time_on_page,
    COUNT(DISTINCT CASE WHEN is_new_user THEN session_id END) AS new_visitors
FROM sessions
WHERE created_at >= NOW() - INTERVAL '90 days'
GROUP BY DATE(created_at);

-- Índice na view materializada
CREATE INDEX idx_mv_dashboard_date ON mv_dashboard_stats(date DESC);

-- Refresh diário (via cron ou script)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_stats;
```

---

### 5. Explain Analyze (Análise de Queries)

```sql
-- Verificar plano de execução
EXPLAIN ANALYZE
SELECT p.*, COUNT(ac.id) AS clicks
FROM posts p
LEFT JOIN post_products pp ON pp.post_id = p.id
LEFT JOIN affiliate_clicks ac ON ac.product_id = pp.product_id
WHERE p.status = 'published'
GROUP BY p.id
ORDER BY clicks DESC
LIMIT 10;

-- Procurar por:
-- - Sequential Scan (ruim, deveria usar índice)
-- - Index Scan (bom)
-- - Nested Loop vs Hash Join (depende do volume)
```

## 📊 Triggers e Funções

### 1. Trigger para Atualizar `updated_at`

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar em todas as tabelas relevantes
CREATE TRIGGER update_posts_updated_at
BEFORE UPDATE ON posts
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

### 2. Trigger para Atualizar Contadores (Desnormalização)

```sql
CREATE OR REPLACE FUNCTION update_product_click_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products
    SET click_count = click_count + 1
    WHERE id = NEW.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_product_clicks
AFTER INSERT ON affiliate_clicks
FOR EACH ROW
EXECUTE FUNCTION update_product_click_count();
```

---

### 3. Função para Calcular CTR de um Post

```sql
CREATE OR REPLACE FUNCTION calculate_post_ctr(p_post_id UUID)
RETURNS NUMERIC AS $$
DECLARE
    v_views INTEGER;
    v_clicks INTEGER;
BEGIN
    -- Contar visualizações
    SELECT COUNT(DISTINCT session_id) INTO v_views
    FROM sessions
    WHERE post_id = p_post_id;

    -- Contar cliques
    SELECT COUNT(*) INTO v_clicks
    FROM affiliate_clicks
    WHERE post_id = p_post_id;

    -- Calcular CTR
    IF v_views = 0 THEN
        RETURN 0;
    ELSE
        RETURN ROUND((v_clicks::NUMERIC / v_views) * 100, 2);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Uso
SELECT calculate_post_ctr('post-uuid-here');
```

## 🔒 Backup e Recovery

### Estratégia de Backup

**Daily Full Backup**:
```bash
# Backup completo diário
pg_dump -h localhost -U postgres -d geekbidu -F c -f /backup/geekbidu_$(date +%Y%m%d).dump

# Backup apenas schema
pg_dump -h localhost -U postgres -d geekbidu -s -f /backup/schema_$(date +%Y%m%d).sql
```

**Continuous Archiving (WAL)**:
```bash
# Configurar no postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
```

**Recovery**:
```bash
# Restaurar backup
pg_restore -h localhost -U postgres -d geekbidu_new /backup/geekbidu_20251210.dump
```

## 📚 Migrations com Alembic

### Criar Migration

```bash
# Criar nova migration
alembic revision -m "add_click_count_to_products"
```

```python
# migrations/versions/xxx_add_click_count.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('products',
        sa.Column('click_count', sa.Integer(), server_default='0', nullable=False)
    )
    op.create_index('idx_products_click_count', 'products', ['click_count'])

def downgrade():
    op.drop_index('idx_products_click_count')
    op.drop_column('products', 'click_count')
```

```bash
# Aplicar migrations
alembic upgrade head
```

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
