from dataclasses import dataclass

from django.db.models import TextChoices


class CategorySlug(TextChoices):
    BUILDS = "builds", "Builds"
    GUIDES = "guides", "Guides"
    REVIEWS = "reviews", "Reviews"


@dataclass(frozen=True)
class StructuralCategory:
    slug: CategorySlug
    name: str
    description: str

    def as_content_dict(self):
        return {
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
        }


STRUCTURAL_CATEGORIES = (
    StructuralCategory(CategorySlug.BUILDS, "Builds", "Motorcycle projects."),
    StructuralCategory(CategorySlug.GUIDES, "Guides", "Practical riding guides."),
    StructuralCategory(CategorySlug.REVIEWS, "Reviews", "Motorcycle reviews."),
)
