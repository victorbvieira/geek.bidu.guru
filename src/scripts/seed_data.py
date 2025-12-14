#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo.

Uso:
    cd src
    python -m scripts.seed_data

Opcoes:
    --clear     Limpa dados existentes antes de inserir
    --force     Executa sem confirmacao

Este script NAO afeta os testes - os testes limpam o banco antes de cada execucao.
"""

import asyncio
import sys
from decimal import Decimal
from pathlib import Path

# Adiciona o diretorio src ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.category import Category
from app.models.product import Product, ProductAvailability, ProductPlatform


# =============================================================================
# Dados de exemplo - Categorias
# =============================================================================

CATEGORIES = [
    {
        "name": "Star Wars",
        "slug": "star-wars",
        "description": "Produtos da franquia Star Wars - action figures, camisetas, canecas e muito mais!",
        "seo_title": "Presentes Star Wars | Produtos Geek",
        "seo_description": "Encontre os melhores presentes Star Wars: Funko Pop, action figures, camisetas e acessorios. Produtos oficiais para fas da saga.",
    },
    {
        "name": "Marvel",
        "slug": "marvel",
        "description": "Produtos do universo Marvel - Vingadores, Homem-Aranha, X-Men e mais!",
        "seo_title": "Presentes Marvel | Produtos Geek",
        "seo_description": "Os melhores presentes Marvel: Funko Pop dos Vingadores, camisetas do Homem-Aranha e action figures. Produtos oficiais.",
    },
    {
        "name": "DC Comics",
        "slug": "dc-comics",
        "description": "Produtos DC Comics - Batman, Superman, Mulher Maravilha e Liga da Justica!",
        "seo_title": "Presentes DC Comics | Produtos Geek",
        "seo_description": "Presentes DC Comics: action figures do Batman, camisetas Superman e produtos da Liga da Justica. Oficiais e exclusivos.",
    },
    {
        "name": "Harry Potter",
        "slug": "harry-potter",
        "description": "Produtos magicos do mundo de Harry Potter - varinhas, casas de Hogwarts e mais!",
        "seo_title": "Presentes Harry Potter | Produtos Geek",
        "seo_description": "Presentes Harry Potter: varinhas magicas, roupas das casas de Hogwarts, Funko Pop e acessorios para bruxos.",
    },
    {
        "name": "Funko Pop",
        "slug": "funko-pop",
        "description": "Colecao de Funko Pop de todas as franquias - Marvel, DC, Star Wars, anime e mais!",
        "seo_title": "Funko Pop | Colecione Seus Personagens Favoritos",
        "seo_description": "Funko Pop de todas as franquias: Marvel, DC, Star Wars, anime, series e filmes. Encontre o Funko perfeito para presentear.",
    },
    {
        "name": "Gamer",
        "slug": "gamer",
        "description": "Produtos para gamers - perifericos, camisetas, action figures de jogos!",
        "seo_title": "Presentes Gamer | Produtos para Jogadores",
        "seo_description": "Presentes para gamers: perifericos, camisetas de jogos, action figures e acessorios. Ideal para quem ama videogames.",
    },
    {
        "name": "Anime",
        "slug": "anime",
        "description": "Produtos de anime - Naruto, Dragon Ball, One Piece, Demon Slayer e mais!",
        "seo_title": "Presentes Anime | Produtos Otaku",
        "seo_description": "Presentes para fas de anime: Funko Pop, action figures, camisetas de Naruto, Dragon Ball, One Piece e mais.",
    },
    {
        "name": "Camisetas",
        "slug": "camisetas",
        "description": "Camisetas geek de todas as franquias - estampas exclusivas e oficiais!",
        "seo_title": "Camisetas Geek | Estampas Exclusivas",
        "seo_description": "Camisetas geek com estampas de Star Wars, Marvel, DC, anime e games. Produtos oficiais e exclusivos.",
    },
]


# =============================================================================
# Dados de exemplo - Produtos
# =============================================================================

PRODUCTS = [
    # Star Wars
    {
        "name": "Funko Pop Star Wars - Darth Vader #01",
        "slug": "funko-pop-darth-vader-01",
        "short_description": "Funko Pop classico do Darth Vader, o vilao mais iconico de Star Wars.",
        "long_description": "O Funko Pop Darth Vader #01 e uma peca de colecao essencial para qualquer fa de Star Wars. Com aproximadamente 10cm de altura, este boneco captura perfeitamente a essencia do Lorde Sith mais temido da galaxia.",
        "price": Decimal("149.90"),
        "platform": ProductPlatform.AMAZON,
        "platform_product_id": "B00BV1P6GY",
        "affiliate_url_raw": "https://www.amazon.com.br/dp/B00BV1P6GY?tag=geekbidu-20",
        "affiliate_redirect_slug": "funko-darth-vader-amazon",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.8"),
        "review_count": 1250,
        "categories": ["star-wars", "funko-pop"],
        "tags": ["funko", "star-wars", "darth-vader", "vilao", "colecao"],
        "images": [
            "https://m.media-amazon.com/images/I/41E6sJG2SQL._AC_SX679_.jpg",
        ],
    },
    {
        "name": "Sabre de Luz Star Wars - Luke Skywalker",
        "slug": "sabre-luz-luke-skywalker",
        "short_description": "Replica do sabre de luz de Luke Skywalker com luz e som.",
        "long_description": "Replica oficial do sabre de luz de Luke Skywalker. Possui luz LED azul e efeitos sonoros ao movimentar. Perfeito para colecao ou cosplay.",
        "price": Decimal("289.90"),
        "platform": ProductPlatform.AMAZON,
        "platform_product_id": "B08XYZLUKE",
        "affiliate_url_raw": "https://www.amazon.com.br/dp/B08XYZLUKE?tag=geekbidu-20",
        "affiliate_redirect_slug": "sabre-luz-luke-amazon",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.6"),
        "review_count": 856,
        "categories": ["star-wars"],
        "tags": ["sabre-de-luz", "star-wars", "luke-skywalker", "replica", "cosplay"],
        "images": [],
    },
    # Marvel
    {
        "name": "Funko Pop Marvel - Homem de Ferro #04",
        "slug": "funko-pop-homem-de-ferro-04",
        "short_description": "Funko Pop do Homem de Ferro na sua armadura classica Mark III.",
        "long_description": "O Funko Pop Homem de Ferro #04 traz Tony Stark em sua iconica armadura vermelha e dourada. Uma peca essencial para colecaoadores Marvel.",
        "price": Decimal("139.90"),
        "platform": ProductPlatform.AMAZON,
        "platform_product_id": "B00BV1IRON",
        "affiliate_url_raw": "https://www.amazon.com.br/dp/B00BV1IRON?tag=geekbidu-20",
        "affiliate_redirect_slug": "funko-homem-ferro-amazon",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.9"),
        "review_count": 2100,
        "categories": ["marvel", "funko-pop"],
        "tags": ["funko", "marvel", "homem-de-ferro", "vingadores", "tony-stark"],
        "images": [
            "https://m.media-amazon.com/images/I/51GRxHzVRlL._AC_SX679_.jpg",
        ],
    },
    {
        "name": "Escudo Capitao America - Replica em Metal",
        "slug": "escudo-capitao-america-metal",
        "short_description": "Replica do escudo do Capitao America em metal de alta qualidade.",
        "long_description": "Replica oficial do escudo do Capitao America em metal. Tamanho real (60cm), perfeito para decoracao ou cosplay. Acompanha suporte de parede.",
        "price": Decimal("599.90"),
        "platform": ProductPlatform.MERCADOLIVRE,
        "platform_product_id": "MLB123456789",
        "affiliate_url_raw": "https://www.mercadolivre.com.br/escudo-capitao-america/p/MLB123456789",
        "affiliate_redirect_slug": "escudo-capitao-ml",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.7"),
        "review_count": 432,
        "categories": ["marvel"],
        "tags": ["marvel", "capitao-america", "escudo", "replica", "metal", "cosplay"],
        "images": [],
    },
    # DC Comics
    {
        "name": "Funko Pop DC - Batman #01",
        "slug": "funko-pop-batman-01",
        "short_description": "Funko Pop classico do Batman, o Cavaleiro das Trevas.",
        "long_description": "O Funko Pop Batman #01 traz o heroi de Gotham em seu traje classico. Uma peca iconica para qualquer colecao DC Comics.",
        "price": Decimal("129.90"),
        "platform": ProductPlatform.AMAZON,
        "platform_product_id": "B00BV1BATM",
        "affiliate_url_raw": "https://www.amazon.com.br/dp/B00BV1BATM?tag=geekbidu-20",
        "affiliate_redirect_slug": "funko-batman-amazon",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.8"),
        "review_count": 1890,
        "categories": ["dc-comics", "funko-pop"],
        "tags": ["funko", "dc", "batman", "gotham", "heroi"],
        "images": [
            "https://m.media-amazon.com/images/I/41mOqzPzKOL._AC_SX679_.jpg",
        ],
    },
    # Harry Potter
    {
        "name": "Varinha Magica Harry Potter - Hermione Granger",
        "slug": "varinha-hermione-granger",
        "short_description": "Replica oficial da varinha de Hermione Granger com caixa Olivaras.",
        "long_description": "Varinha oficial de Hermione Granger da colecao Warner Bros. Vem na caixa estilo Olivaras. Material: resina de alta qualidade. Tamanho: 38cm.",
        "price": Decimal("189.90"),
        "platform": ProductPlatform.AMAZON,
        "platform_product_id": "B07HPWAND1",
        "affiliate_url_raw": "https://www.amazon.com.br/dp/B07HPWAND1?tag=geekbidu-20",
        "affiliate_redirect_slug": "varinha-hermione-amazon",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.9"),
        "review_count": 756,
        "categories": ["harry-potter"],
        "tags": ["harry-potter", "hermione", "varinha", "hogwarts", "bruxo"],
        "images": [],
    },
    {
        "name": "Cachecol Grifinoria Harry Potter",
        "slug": "cachecol-grifinoria",
        "short_description": "Cachecol oficial da Grifinoria nas cores vermelho e dourado.",
        "long_description": "Cachecol oficial da casa Grifinoria de Hogwarts. Cores vermelho e dourado, material: acrilico macio. Tamanho: 150cm x 20cm. Produto licenciado Warner Bros.",
        "price": Decimal("79.90"),
        "platform": ProductPlatform.SHOPEE,
        "platform_product_id": "SH987654321",
        "affiliate_url_raw": "https://shopee.com.br/cachecol-grifinoria-i.987654321",
        "affiliate_redirect_slug": "cachecol-grifinoria-shopee",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.5"),
        "review_count": 1234,
        "categories": ["harry-potter", "camisetas"],
        "tags": ["harry-potter", "grifinoria", "cachecol", "hogwarts", "inverno"],
        "images": [],
    },
    # Gamer
    {
        "name": "Mouse Gamer Logitech G502 HERO",
        "slug": "mouse-logitech-g502-hero",
        "short_description": "Mouse gamer de alta performance com sensor HERO 25K.",
        "long_description": "O Logitech G502 HERO possui sensor HERO 25K com ate 25.600 DPI, 11 botoes programaveis, sistema de peso ajustavel e RGB LIGHTSYNC. O mouse gamer mais vendido do mundo.",
        "price": Decimal("299.90"),
        "platform": ProductPlatform.AMAZON,
        "platform_product_id": "B07GBZ4Q68",
        "affiliate_url_raw": "https://www.amazon.com.br/dp/B07GBZ4Q68?tag=geekbidu-20",
        "affiliate_redirect_slug": "mouse-g502-amazon",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.9"),
        "review_count": 45678,
        "categories": ["gamer"],
        "tags": ["mouse", "gamer", "logitech", "g502", "rgb", "periferico"],
        "images": [
            "https://m.media-amazon.com/images/I/61mpMH5TzkL._AC_SX679_.jpg",
        ],
    },
    {
        "name": "Headset Gamer HyperX Cloud II",
        "slug": "headset-hyperx-cloud-2",
        "short_description": "Headset gamer com som surround 7.1 virtual e microfone destacavel.",
        "long_description": "O HyperX Cloud II oferece som surround 7.1 virtual, drivers de 53mm, microfone com cancelamento de ruido destacavel e espuma de memoria nas almofadas. Compativel com PC, PS4, PS5, Xbox e Switch.",
        "price": Decimal("449.90"),
        "platform": ProductPlatform.MERCADOLIVRE,
        "platform_product_id": "MLB987654321",
        "affiliate_url_raw": "https://www.mercadolivre.com.br/hyperx-cloud-ii/p/MLB987654321",
        "affiliate_redirect_slug": "headset-hyperx-ml",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.8"),
        "review_count": 12345,
        "categories": ["gamer"],
        "tags": ["headset", "gamer", "hyperx", "cloud-ii", "som-surround"],
        "images": [],
    },
    # Anime
    {
        "name": "Funko Pop Naruto - Naruto Uzumaki #71",
        "slug": "funko-pop-naruto-uzumaki",
        "short_description": "Funko Pop do Naruto Uzumaki correndo com kunai.",
        "long_description": "O Funko Pop Naruto #71 traz o protagonista do anime em pose de corrida segurando uma kunai. Uma peca essencial para fas do ninja de Konoha.",
        "price": Decimal("159.90"),
        "platform": ProductPlatform.AMAZON,
        "platform_product_id": "B07NARUTO1",
        "affiliate_url_raw": "https://www.amazon.com.br/dp/B07NARUTO1?tag=geekbidu-20",
        "affiliate_redirect_slug": "funko-naruto-amazon",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.9"),
        "review_count": 3456,
        "categories": ["anime", "funko-pop"],
        "tags": ["funko", "naruto", "anime", "ninja", "konoha"],
        "images": [
            "https://m.media-amazon.com/images/I/41QWMxLOZtL._AC_SX679_.jpg",
        ],
    },
    {
        "name": "Action Figure Dragon Ball - Goku Super Saiyajin",
        "slug": "action-figure-goku-ssj",
        "short_description": "Action figure articulada do Goku Super Saiyajin.",
        "long_description": "Action figure do Goku Super Saiyajin da linha S.H. Figuarts. Altura: 14cm, totalmente articulada com maos e rostos intercambiaveis. Acompanha base e efeitos de energia.",
        "price": Decimal("349.90"),
        "platform": ProductPlatform.AMAZON,
        "platform_product_id": "B08DBZGOKU",
        "affiliate_url_raw": "https://www.amazon.com.br/dp/B08DBZGOKU?tag=geekbidu-20",
        "affiliate_redirect_slug": "goku-ssj-amazon",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.7"),
        "review_count": 2345,
        "categories": ["anime"],
        "tags": ["dragon-ball", "goku", "super-saiyajin", "action-figure", "anime"],
        "images": [],
    },
    # Camisetas
    {
        "name": "Camiseta Star Wars - Logo Classico",
        "slug": "camiseta-star-wars-logo",
        "short_description": "Camiseta preta com logo classico amarelo de Star Wars.",
        "long_description": "Camiseta oficial Star Wars com o logo classico amarelo. Material: 100% algodao, estampa silk screen de alta qualidade. Disponivel nos tamanhos P, M, G e GG.",
        "price": Decimal("79.90"),
        "platform": ProductPlatform.SHOPEE,
        "platform_product_id": "SHSTARWARS1",
        "affiliate_url_raw": "https://shopee.com.br/camiseta-star-wars-i.SHSTARWARS1",
        "affiliate_redirect_slug": "camiseta-sw-shopee",
        "availability": ProductAvailability.AVAILABLE,
        "rating": Decimal("4.6"),
        "review_count": 5678,
        "categories": ["star-wars", "camisetas"],
        "tags": ["camiseta", "star-wars", "logo", "classico", "preta"],
        "images": [],
    },
]


async def clear_data(session: AsyncSession) -> None:
    """Limpa dados existentes (exceto usuarios)."""
    print("Limpando dados existentes...")

    # Ordem correta para evitar erros de FK
    tables = [
        "affiliate_clicks",
        "post_products",
        "posts",
        "products",
        "categories",
    ]

    for table in tables:
        try:
            await session.execute(text(f"DELETE FROM {table}"))
            print(f"  - Tabela {table} limpa")
        except Exception as e:
            print(f"  - Erro ao limpar {table}: {e}")

    await session.commit()
    print("Dados limpos com sucesso!\n")


async def seed_categories(session: AsyncSession) -> dict[str, Category]:
    """Cria categorias de exemplo."""
    print("Criando categorias...")

    categories_by_slug = {}

    for cat_data in CATEGORIES:
        # Verifica se ja existe
        result = await session.execute(
            text("SELECT id FROM categories WHERE slug = :slug"),
            {"slug": cat_data["slug"]},
        )
        existing = result.fetchone()

        if existing:
            print(f"  - {cat_data['name']} (ja existe)")
            # Busca a categoria existente
            result = await session.execute(
                text("SELECT * FROM categories WHERE slug = :slug"),
                {"slug": cat_data["slug"]},
            )
            row = result.fetchone()
            category = Category(
                id=row.id,
                name=row.name,
                slug=row.slug,
            )
        else:
            category = Category(**cat_data)
            session.add(category)
            print(f"  + {cat_data['name']}")

        categories_by_slug[cat_data["slug"]] = category

    await session.commit()
    print(f"Total: {len(CATEGORIES)} categorias\n")

    return categories_by_slug


async def seed_products(
    session: AsyncSession, categories_by_slug: dict[str, Category]
) -> None:
    """Cria produtos de exemplo."""
    print("Criando produtos...")

    created = 0
    skipped = 0

    for prod_data in PRODUCTS:
        # Verifica se ja existe
        result = await session.execute(
            text("SELECT id FROM products WHERE slug = :slug"),
            {"slug": prod_data["slug"]},
        )
        existing = result.fetchone()

        if existing:
            print(f"  - {prod_data['name'][:40]}... (ja existe)")
            skipped += 1
            continue

        # Extrai categorias e converte para lista de slugs
        category_slugs = prod_data.pop("categories", [])

        # Cria produto
        product = Product(**prod_data)
        product.categories = category_slugs  # Armazena slugs no JSONB

        session.add(product)
        print(f"  + {prod_data['name'][:40]}...")
        created += 1

    await session.commit()
    print(f"Total: {created} criados, {skipped} ja existiam\n")


async def main(clear: bool = False, force: bool = False) -> None:
    """Executa o seed do banco de dados."""
    print("\n" + "=" * 60)
    print("SEED DE DADOS - geek.bidu.guru")
    print("=" * 60 + "\n")

    # Verifica ambiente
    database_url = settings.database_url
    if not database_url:
        print("ERRO: DATABASE_URL nao configurada!")
        sys.exit(1)

    # Alerta de seguranca
    if "prod" in database_url.lower():
        print("ATENCAO: Voce esta conectado ao banco de PRODUCAO!")
        if not force:
            response = input("Deseja continuar? (s/N): ")
            if response.lower() != "s":
                print("Operacao cancelada.")
                sys.exit(0)

    print(f"Banco: {database_url.split('@')[-1]}\n")

    # Cria conexao
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Limpa dados se solicitado
        if clear:
            if not force:
                response = input("Limpar dados existentes? (s/N): ")
                if response.lower() != "s":
                    print("Limpeza cancelada.\n")
                else:
                    await clear_data(session)
            else:
                await clear_data(session)

        # Cria categorias
        categories = await seed_categories(session)

        # Cria produtos
        await seed_products(session, categories)

    await engine.dispose()

    print("=" * 60)
    print("SEED CONCLUIDO!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Popula o banco com dados de exemplo")
    parser.add_argument(
        "--clear", action="store_true", help="Limpa dados existentes antes de inserir"
    )
    parser.add_argument(
        "--force", action="store_true", help="Executa sem confirmacao"
    )

    args = parser.parse_args()

    asyncio.run(main(clear=args.clear, force=args.force))
