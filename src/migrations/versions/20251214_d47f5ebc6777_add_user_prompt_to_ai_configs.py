"""add user_prompt to ai_configs

Revision ID: d47f5ebc6777
Revises: 011
Create Date: 2025-12-14 11:55:26.504426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd47f5ebc6777'
down_revision: Union[str, None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Templates de user_prompt com placeholders para cada use_case
USER_PROMPT_TEMPLATES = {
    'post_tags': '''Titulo: {{title}}

Subtitulo: {{subtitle}}

Conteudo:
{{content}}''',

    'post_seo_keyword': '''Titulo: {{title}}

Subtitulo: {{subtitle}}

Conteudo:
{{content}}''',

    'post_seo_title': '''Titulo: {{title}}

Subtitulo: {{subtitle}}

Conteudo:
{{content}}''',

    'post_seo_description': '''Titulo: {{title}}

Subtitulo: {{subtitle}}

Conteudo:
{{content}}''',

    'post_seo_all': '''Titulo: {{title}}

Subtitulo: {{subtitle}}

Conteudo:
{{content}}''',

    'post_content': '''Titulo: {{title}}

Subtitulo: {{subtitle}}

Categoria: {{category}}''',

    'seo_title': '''Titulo: {{title}}

Conteudo:
{{content}}''',

    'seo_description': '''Titulo: {{title}}

Conteudo:
{{content}}''',

    'seo_keywords': '''Titulo: {{title}}

Conteudo:
{{content}}''',

    'product_description': '''Produto: {{product_name}}

Categoria: {{category}}

Informacoes:
{{content}}''',

    'social_share': '''Titulo: {{title}}

Conteudo:
{{content}}''',
}


def upgrade() -> None:
    """Upgrade database schema."""
    # Adiciona coluna user_prompt
    op.add_column('ai_configs', sa.Column('user_prompt', sa.Text(), nullable=True))

    # Atualiza os user_prompts existentes com os templates
    connection = op.get_bind()
    for use_case, template in USER_PROMPT_TEMPLATES.items():
        connection.execute(
            sa.text("""
                UPDATE ai_configs
                SET user_prompt = :template
                WHERE use_case = :use_case
            """),
            {'template': template, 'use_case': use_case}
        )


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column('ai_configs', 'user_prompt')
