import re
import unicodedata
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Category, Post, is_reserved_post_slug

PROVISIONAL_TEXT_MARKERS = ("lorem ipsum", "todo", "tbd", "placeholder")


def clean_text(value, *, field):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError({field: "A non-empty text value is required."})

    value = unicodedata.normalize("NFC", value).replace("\r\n", "\n").strip()
    if "\ufffd" in value or any(
        ord(char) < 32 and char not in "\n\t" for char in value
    ):
        raise ValidationError(
            {field: "The text contains invalid encoding or control characters."}
        )
    if any(marker in value.lower() for marker in PROVISIONAL_TEXT_MARKERS):
        raise ValidationError({field: "Provisional text is not importable."})
    return value


def parse_published_at(value):
    if isinstance(value, datetime):
        return value
    parsed = parse_datetime(value) if isinstance(value, str) else None
    if parsed is None:
        raise ValidationError({"published_at": "Use an ISO 8601 datetime."})
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    return parsed


def import_selected_content(payload, *, author, dry_run=False):
    if author.is_staff or author.is_superuser:
        raise ValidationError(
            "Selected content cannot be assigned to a privileged user."
        )
    if not isinstance(payload, dict):
        raise ValidationError("The import document must be a JSON object.")

    categories = payload.get("categories", [])
    posts = payload.get("posts", [])
    if not isinstance(categories, list) or not isinstance(posts, list):
        raise ValidationError("Categories and posts must be lists.")

    seen_slugs = set()
    prepared_categories = []
    for item in categories:
        slug = item.get("slug", "") if isinstance(item, dict) else ""
        name = item.get("name", "") if isinstance(item, dict) else ""
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValidationError({"category.slug": "Use a lowercase URL slug."})
        prepared_categories.append(
            (slug, clean_text(name, field="category.name"), item.get("description", ""))
        )

    prepared_posts = []
    for item in posts:
        if not isinstance(item, dict):
            raise ValidationError("Each post must be an object.")
        forbidden = {
            "author",
            "author_id",
            "password",
            "featured_image",
            "featured_image_alt",
            "image",
        } & item.keys()
        if forbidden:
            raise ValidationError(
                f"Unsupported import fields: {', '.join(sorted(forbidden))}."
            )
        slug = item.get("slug", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen_slugs:
            raise ValidationError(
                {"post.slug": "Each post needs a unique lowercase URL slug."}
            )
        if is_reserved_post_slug(slug):
            raise ValidationError(
                {"post.slug": "This slug is reserved for an application route."}
            )
        seen_slugs.add(slug)
        category_slugs = item.get("categories", [])
        if not category_slugs or not all(
            isinstance(value, str) for value in category_slugs
        ):
            raise ValidationError(
                {"post.categories": "At least one category slug is required."}
            )
        prepared_posts.append(
            {
                "slug": slug,
                "title": clean_text(item.get("title"), field="post.title"),
                "excerpt": clean_text(item.get("excerpt"), field="post.excerpt"),
                "content": clean_text(item.get("content"), field="post.content"),
                "categories": category_slugs,
                "published_at": parse_published_at(item.get("published_at")),
            }
        )

    if dry_run:
        return {"categories": len(prepared_categories), "posts": len(prepared_posts)}

    for slug, name, description in prepared_categories:
        Category.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": clean_text(description, field="category.description")
                if description
                else "",
            },
        )

    for item in prepared_posts:
        if Post.objects.filter(slug=item["slug"]).exclude(featured_image="").exists():
            raise ValidationError(
                {"post.slug": "Review and remove existing images before importing."}
            )
        categories = list(Category.objects.filter(slug__in=item["categories"]))
        if len(categories) != len(set(item["categories"])):
            raise ValidationError(
                {"post.categories": "Every category slug must exist."}
            )
        post, _ = Post.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "title": item["title"],
                "excerpt": item["excerpt"],
                "content": item["content"],
                "author": author,
                "status": Post.Status.PUBLISHED,
                "published_at": item["published_at"],
            },
        )
        post.categories.set(categories)
    return {"categories": len(prepared_categories), "posts": len(prepared_posts)}
