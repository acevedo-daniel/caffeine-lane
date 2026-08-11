from django.utils.translation import gettext


def category_label(category):
    """Return a localized label for the site's structural taxonomy."""

    labels = {
        "builds": gettext("Builds"),
        "guides": gettext("Guides"),
        "reviews": gettext("Reviews"),
    }
    return labels.get(category.slug, category.name)
