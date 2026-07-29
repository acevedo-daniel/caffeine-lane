from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.accounts.models import User
from apps.posts.models import Category, Post
from apps.posts.taxonomy import STRUCTURAL_CATEGORIES, CategorySlug

RESERVED_SLIDER_ASSET = "source/reserved-slider/reserved-slider-01.webp"

PORTFOLIO_POSTS = (
    {
        "slug": "cafe-racer-de-garaje",
        "title": "Café racer de garaje: una base honesta",
        "excerpt": "Decisiones simples para convertir una base usada en una moto que quieras seguir manejando.",
        "content": "El proyecto empezó por la postura y la confiabilidad. Antes de comprar piezas, ordenamos frenos, cableado y ergonomía para que cada cambio sumara kilómetros y no problemas.",
        "category": CategorySlug.BUILDS,
        "published_at": "2026-02-03T12:00:00+00:00",
        "image": "source/builds/build-01.webp",
        "alt": "Café racer negra en restauración dentro de un taller luminoso.",
    },
    {
        "slug": "frenos-antes-de-potencia",
        "title": "Frenos antes de potencia",
        "excerpt": "La mejora que más transforma una moto vieja no siempre está en el motor.",
        "content": "Revisamos mangueras, líquido, pastillas y tacto de maneta. Una frenada consistente da margen para disfrutar una ruta y permite evaluar el resto de la moto con calma.",
        "category": CategorySlug.BUILDS,
        "published_at": "2026-02-10T12:00:00+00:00",
        "image": "source/builds/build-02.webp",
        "alt": "Detalle de una café racer preparada en un banco de trabajo.",
    },
    {
        "slug": "cableado-que-se-puede-reparar",
        "title": "Cableado que se puede reparar al costado de la ruta",
        "excerpt": "Un arnés claro y documentado es una mejora de seguridad, no un detalle estético.",
        "content": "Etiquetamos circuitos, protegimos uniones y dejamos conectores accesibles. El objetivo es encontrar un fallo sin desmontar media moto ni depender de memoria.",
        "category": CategorySlug.BUILDS,
        "published_at": "2026-02-17T12:00:00+00:00",
        "image": "source/builds/build-03.webp",
        "alt": "Motocicleta café racer y herramientas ordenadas en un taller.",
    },
    {
        "slug": "asiento-y-postura-para-rutas-cortas",
        "title": "Asiento y postura para rutas cortas",
        "excerpt": "Cómo encontrar una posición compacta sin convertir cada salida en una negociación con la espalda.",
        "content": "Probamos altura de estriberas, alcance al manillar y densidad de espuma. Una postura equilibrada hace que una moto baja se sienta precisa también después de dos horas.",
        "category": CategorySlug.BUILDS,
        "published_at": "2026-02-24T12:00:00+00:00",
        "image": "source/builds/build-04.webp",
        "alt": "Café racer de perfil en un taller de restauración.",
    },
    {
        "slug": "checklist-para-salir-el-fin-de-semana",
        "title": "Checklist para salir el fin de semana",
        "excerpt": "Una rutina de diez minutos para arrancar con menos sorpresas y más ganas de rodar.",
        "content": "Neumáticos, luces, combustible, documentación y pronóstico forman el mínimo. Sumamos agua, capas livianas y una herramienta que realmente sepas usar.",
        "category": CategorySlug.GUIDES,
        "published_at": "2026-03-03T12:00:00+00:00",
        "image": "source/guides/guide-01.webp",
        "alt": "Café racer preparada junto a una ruta de montaña al amanecer.",
    },
    {
        "slug": "mapa-papel-y-ruta-secundaria",
        "title": "Mapa de papel y ruta secundaria",
        "excerpt": "Elegir caminos tranquilos vuelve más memorable una salida incluso cuando el destino es cercano.",
        "content": "Las rutas secundarias exigen menos prisa y más atención. Marcamos paradas, estaciones de servicio y un plan alternativo antes de dejar la ciudad.",
        "category": CategorySlug.GUIDES,
        "published_at": "2026-03-10T12:00:00+00:00",
        "image": "source/guides/guide-02.webp",
        "alt": "Motocicleta junto a una carretera de montaña y un mapa de ruta.",
    },
    {
        "slug": "como-fotografiar-tu-moto-sin-estudio",
        "title": "Cómo fotografiar tu moto sin estudio",
        "excerpt": "Luz suave, fondo simple y un encuadre bajo bastan para mostrar las proporciones reales.",
        "content": "Buscá las últimas horas de la tarde, limpiá el encuadre y evitá los fondos cargados. Una foto útil cuenta cómo se ve la moto y también dónde te llevó.",
        "category": CategorySlug.GUIDES,
        "published_at": "2026-03-17T12:00:00+00:00",
        "image": "source/guides/guide-03.webp",
        "alt": "Café racer estacionada frente a un paisaje de montaña sereno.",
    },
    {
        "slug": "review-una-cafe-racer-para-la-ciudad",
        "title": "Review: una café racer para la ciudad",
        "excerpt": "Ágil, ligera y directa: qué se gana y qué se resigna al usarla todos los días.",
        "content": "En ciudad importan el radio de giro, el calor y la respuesta a baja velocidad. Esta configuración prioriza control y una mecánica fácil de mantener.",
        "category": CategorySlug.REVIEWS,
        "published_at": "2026-03-24T12:00:00+00:00",
        "image": "source/reviews/review-01.webp",
        "alt": "Café racer junto a un camino costero al atardecer azul.",
    },
    {
        "slug": "review-viajar-liviano-en-dos-ruedas",
        "title": "Review: viajar liviano en dos ruedas",
        "excerpt": "Una prueba de equipaje mínimo para escapadas de una noche sin cargar la moto de más.",
        "content": "Con una mochila compacta y herramientas básicas la moto conserva su manejo. La clave es decidir qué necesitás antes de salir, no comprar soluciones de último momento.",
        "category": CategorySlug.REVIEWS,
        "published_at": "2026-03-31T12:00:00+00:00",
        "image": "source/reviews/review-02.webp",
        "alt": "Motocicleta café racer frente al horizonte del mar.",
    },
    {
        "slug": "review-cuando-un-proyecto-ya-esta-listo",
        "title": "Review: cuándo un proyecto ya está listo",
        "excerpt": "No existe el último tornillo perfecto; sí existe el momento de salir a manejar.",
        "content": "Probamos la moto en trayectos conocidos y anotamos solo lo que afecta seguridad, confort o confiabilidad. El resto puede evolucionar con el uso y las historias.",
        "category": CategorySlug.REVIEWS,
        "published_at": "2026-04-07T12:00:00+00:00",
        "image": "source/reviews/review-03.webp",
        "alt": "Café racer estacionada en un mirador de costa al anochecer.",
    },
)


class Command(BaseCommand):
    help = "Create the idempotent public portfolio dataset and upload its images."

    def handle(self, *args, **options):
        assets_dir = Path(settings.BASE_DIR) / "static" / "images" / "portfolio"
        missing_assets = sorted(
            {
                item["image"]
                for item in PORTFOLIO_POSTS
                if not (assets_dir / item["image"]).is_file()
            }
        )
        if missing_assets:
            raise CommandError("Missing portfolio assets: " + ", ".join(missing_assets))

        with transaction.atomic():
            author, _ = User.objects.get_or_create(
                email="portfolio-author@example.invalid",
                defaults={
                    "username": "portfolio-author",
                    "display_name": "Caffeine Lane",
                },
            )
            author.is_staff = False
            author.is_superuser = False
            author.set_unusable_password()
            author.save(update_fields=["is_staff", "is_superuser", "password"])

            categories = {}
            for category in STRUCTURAL_CATEGORIES:
                categories[category.slug], _ = Category.objects.update_or_create(
                    slug=category.slug,
                    defaults={
                        "name": category.name,
                        "description": category.description,
                    },
                )

            for item in PORTFOLIO_POSTS:
                post, _ = Post.objects.update_or_create(
                    slug=item["slug"],
                    defaults={
                        "title": item["title"],
                        "excerpt": item["excerpt"],
                        "content": item["content"],
                        "author": author,
                        "status": Post.Status.PUBLISHED,
                        "published_at": parse_datetime(item["published_at"]),
                        "featured_image_alt": item["alt"],
                    },
                )
                post.categories.set([categories[item["category"]]])
                if not post.featured_image:
                    asset_path = assets_dir / item["image"]
                    post.featured_image.save(
                        item["image"], ContentFile(asset_path.read_bytes()), save=True
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Portfolio ready: {len(STRUCTURAL_CATEGORIES)} categories and "
                f"{len(PORTFOLIO_POSTS)} posts."
            )
        )
