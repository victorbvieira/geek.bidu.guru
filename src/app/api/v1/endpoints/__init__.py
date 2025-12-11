"""
API v1 endpoints.

Este pacote contém todos os endpoints REST da API v1 do geek.bidu.guru.

Módulos disponíveis:
    - users: Gerenciamento de usuários (admin, editor, author)
    - categories: Gerenciamento de categorias do blog
    - posts: Gerenciamento de posts/artigos
    - products: Gerenciamento de produtos de afiliados
    - newsletter: Inscrição e gerenciamento de newsletter
    - clicks: Tracking de cliques e redirects de afiliados

Estrutura dos endpoints:
    Cada módulo segue o padrão REST:
    - GET    /{resource}       - Lista com paginação
    - GET    /{resource}/{id}  - Busca por ID
    - POST   /{resource}       - Cria novo
    - PATCH  /{resource}/{id}  - Atualiza existente
    - DELETE /{resource}/{id}  - Remove

Autenticação:
    TODO: Implementar JWT para endpoints administrativos.
    Endpoints públicos (newsletter/subscribe, clicks/go) não requerem auth.

Versionamento:
    A API é versionada via prefixo de URL (/api/v1/).
    Novas versões serão adicionadas como /api/v2/, /api/v3/, etc.
"""
