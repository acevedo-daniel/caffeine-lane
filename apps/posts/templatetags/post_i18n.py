from django import template

from apps.posts.presentation import category_label

register = template.Library()


@register.filter
def localized_category(category):
    return category_label(category)
