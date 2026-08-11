from .taxonomy import STRUCTURAL_CATEGORIES


def navigation_categories(request):
    return {"navigation_categories": STRUCTURAL_CATEGORIES}
