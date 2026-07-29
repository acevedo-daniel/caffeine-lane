from django.db import migrations


STRUCTURAL_CATEGORIES = (
    ("builds", "Builds", "Motorcycle projects."),
    ("guides", "Guides", "Practical riding guides."),
    ("reviews", "Reviews", "Motorcycle reviews."),
)


def create_structural_categories(apps, schema_editor):
    Category = apps.get_model("posts", "Category")
    for slug, name, description in STRUCTURAL_CATEGORIES:
        Category.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "description": description},
        )


class Migration(migrations.Migration):
    dependencies = [("posts", "0006_alter_category_image_alter_post_featured_image")]

    operations = [
        migrations.RunPython(create_structural_categories, migrations.RunPython.noop)
    ]
