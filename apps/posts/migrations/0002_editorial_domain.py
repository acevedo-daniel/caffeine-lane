import apps.posts.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


def set_published_dates(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    Post.objects.filter(status="published", published_at__isnull=True).update(
        published_at=models.F("created_at")
    )


class Migration(migrations.Migration):
    dependencies = [("posts", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="category",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="category",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name="post", old_name="image", new_name="featured_image"
        ),
        migrations.RenameField(
            model_name="post", old_name="category", new_name="categories"
        ),
        migrations.AddField(
            model_name="post",
            name="excerpt",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name="post",
            name="featured_image_alt",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="post",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(set_published_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="category",
            name="image",
            field=models.ImageField(blank=True, upload_to="categories/"),
        ),
        migrations.AlterField(
            model_name="comment",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="categories",
            field=models.ManyToManyField(related_name="posts", to="posts.category"),
        ),
        migrations.AlterField(
            model_name="post",
            name="featured_image",
            field=models.ImageField(blank=True, upload_to=apps.posts.models.post_image_path),
        ),
        migrations.AlterField(
            model_name="post",
            name="slug",
            field=models.SlugField(blank=True, max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("published", "Published")],
                default="draft",
                max_length=10,
            ),
        ),
        migrations.AlterModelOptions(
            name="post", options={"ordering": ["-published_at", "-created_at"]}
        ),
        migrations.AddConstraint(
            model_name="post",
            constraint=models.CheckConstraint(
                condition=Q(status="draft") | Q(published_at__isnull=False),
                name="published_post_requires_date",
            ),
        ),
    ]
