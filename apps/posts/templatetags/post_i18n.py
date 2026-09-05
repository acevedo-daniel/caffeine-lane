import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.posts.presentation import category_label

register = template.Library()


@register.filter
def localized_category(category):
    return category_label(category)


@register.filter
def reading_time(post):
    if hasattr(post, "reading_time"):
        return post.reading_time
    words = len(str(post).split())
    return max(1, round(words / 200))


@register.filter
def highlight_search(text, query):
    """Safely highlight matching query tokens in text."""
    if not text or not query:
        return text

    terms = [re.escape(term.strip()) for term in str(query).split() if term.strip()]
    if not terms:
        return text

    pattern = re.compile(r"(" + "|".join(terms) + r")", re.IGNORECASE)
    escaped_text = escape(str(text))
    highlighted = pattern.sub(r'<mark class="search-highlight">\1</mark>', escaped_text)
    return mark_safe(highlighted)
