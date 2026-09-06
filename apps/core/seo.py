import json

from django.conf import settings
from django.templatetags.static import static
from django.utils import timezone
from django.utils.safestring import mark_safe

SITE_NAME = "Caffeine Lane"
DEFAULT_DESCRIPTION = (
    "Editorial journal for cafe racer builds, practical workshop guides, reviews, "
    "and rider culture."
)
DEFAULT_DESCRIPTION_ES = (
    "Publicación editorial sobre cafe racers, guías prácticas de taller, reseñas "
    "y cultura motociclista."
)


def localized_copy(request, spanish, english):
    language = getattr(request, "LANGUAGE_CODE", "es") or "es"
    return spanish if language.startswith("es") else english


def public_site_url(request):
    configured_url = settings.PUBLIC_SITE_URL.rstrip("/")
    return configured_url or request.build_absolute_uri("/").rstrip("/")


def absolute_url(request, path):
    if path.startswith(("http://", "https://")):
        return path
    return f"{public_site_url(request)}/{path.lstrip('/')}"


def json_ld(payload):
    serialized = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return mark_safe(serialized)


def website_schema(request):
    return json_ld(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": public_site_url(request),
            "description": localized_copy(
                request, DEFAULT_DESCRIPTION_ES, DEFAULT_DESCRIPTION
            ),
            "inLanguage": ["es", "en"],
        }
    )


def article_schema(request, post):
    image_url = (
        absolute_url(request, post.featured_image.url)
        if post.featured_image
        else absolute_url(
            request, static("images/brand/character/character-welcome.webp")
        )
    )
    published_at = post.published_at or timezone.now()
    return json_ld(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": post.title,
            "description": post.excerpt or post.content[:160],
            "image": [image_url],
            "datePublished": published_at.isoformat(),
            "dateModified": post.updated_at.isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": absolute_url(request, post.get_absolute_url()),
            },
            "author": {
                "@type": "Person",
                "name": post.author.display_name or post.author.username,
            },
            "publisher": {"@type": "Organization", "name": SITE_NAME},
        }
    )


def seo_defaults(request):
    path = request.path
    noindex_prefixes = (
        "/accounts/",
        "/admin/",
        "/csp-report/",
        "/posts/comments/",
        "/posts/new/",
        "/400/",
        "/403/",
        "/404/",
        "/500/",
    )
    noindex = (
        path == "/contact/"
        or path == "/posts/search/"
        or path.startswith(noindex_prefixes)
    )
    language = getattr(request, "LANGUAGE_CODE", None) or "es"
    locale = "es_AR" if language.startswith("es") else "en_US"
    alternate_locale = "en_US" if locale == "es_AR" else "es_AR"
    canonical_url = absolute_url(request, path)
    default_image_url = absolute_url(
        request, static("images/brand/character/character-welcome.webp")
    )

    return {
        "seo_canonical_url": canonical_url,
        "seo_site_url": public_site_url(request),
        "seo_default_title": SITE_NAME,
        "seo_default_description": localized_copy(
            request, DEFAULT_DESCRIPTION_ES, DEFAULT_DESCRIPTION
        ),
        "seo_default_image_url": default_image_url,
        "seo_image_alt": SITE_NAME,
        "seo_robots": "noindex, nofollow" if noindex else "index, follow",
        "seo_locale": locale,
        "seo_alternate_locale": alternate_locale,
    }
