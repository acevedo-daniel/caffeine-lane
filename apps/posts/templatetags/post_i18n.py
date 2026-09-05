from django import template

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
