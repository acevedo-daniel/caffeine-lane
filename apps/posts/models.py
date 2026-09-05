import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.image_validators import validate_uploaded_image

RESERVED_POST_SLUGS = {"search", "new"}


def is_reserved_post_slug(slug):
    return slug.lower() in RESERVED_POST_SLUGS


def post_image_path(instance, filename):
    extension = os.path.splitext(filename)[1]
    return f"posts/media/{instance.slug or 'draft'}{extension}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="categories/", blank=True, validators=[validate_uploaded_image]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED, published_at__isnull=False)

    def with_author(self):
        return self.select_related("author")

    def with_categories(self):
        return self.prefetch_related("categories")

    def for_listing(self):
        return self.published().with_author().with_categories()


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(
        upload_to=post_image_path, blank=True, validators=[validate_uploaded_image]
    )
    featured_image_alt = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    categories = models.ManyToManyField(Category, related_name="posts")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    def clean(self):
        if self.slug and is_reserved_post_slug(self.slug):
            raise ValidationError(
                {"slug": _("This slug is reserved for an application route.")}
            )
        if self.status == self.Status.PUBLISHED and not self.published_at:
            raise ValidationError(
                {"published_at": _("Published posts require a date.")}
            )
        if self.featured_image and not self.featured_image_alt:
            raise ValidationError(
                {"featured_image_alt": _("Visible images require alternative text.")}
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "post"
            candidate = base_slug
            counter = 2
            while is_reserved_post_slug(candidate) or (
                type(self).objects.exclude(pk=self.pk).filter(slug=candidate).exists()
            ):
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate
        elif is_reserved_post_slug(self.slug):
            raise ValidationError(
                {"slug": _("This slug is reserved for an application route.")}
            )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    @property
    def reading_time(self):
        words = len(self.content.split())
        return max(1, round(words / 200))

    @property
    def build_specs(self):
        """Return technical build specifications dictionary for build posts, or None."""
        if not self.categories.filter(slug="builds").exists():
            return None

        title_lower = self.title.lower()
        if "frenos" in title_lower:
            return {
                "donor": "Yamaha SR500",
                "displacement": "499 cc Single Cylinder",
                "frame": "Original semi-double cradle, lightened and de-tabbed",
                "front_brake": "Dual 298mm drilled discs with Brembo 2-piston calipers",
                "rear_brake": "Upgraded ventilated drum with custom linkage",
                "exhaust": "SuperTrapp stainless steel 1.75-inch reverse cone",
            }
        elif "cableado" in title_lower:
            return {
                "donor": "Moto Guzzi Le Mans II",
                "displacement": "844 cc 90° V-Twin",
                "frame": "Lino Tonti spine frame, brushed satin finish",
                "carburetor": "Dell'Orto PHF 36mm pumper carbs",
                "electrical": "Custom simplified loom with solid-state control module",
                "exhaust": "Lafranconi Competizione stainless dual pipes",
            }
        elif "asiento" in title_lower or "postura" in title_lower:
            return {
                "donor": "Honda CB550 Four",
                "displacement": "544 cc SOHC Air-Cooled Inline-Four",
                "frame": "Shortened rear subframe with integrated LED hoop",
                "seat": "Hand-shaped high-density foam with distressed cognac leather",
                "cockpit": "Tommaselli clip-ons, Tarozzi rearsets",
                "exhaust": "4-into-1 ceramic black header with reverse cone",
            }
        else:
            return {
                "donor": "1978 Honda CB750 Four",
                "displacement": "736 cc SOHC Inline-Four",
                "frame": "Custom rear loop, de-tabbed and powder-coated satin black",
                "carburetor": "Keihin 28mm rebuilt with velocity stacks and brass jets",
                "exhaust": "Custom 4-into-1 raw stainless steel with megaphone muffler",
                "suspension": "Showa 35mm lowered 30mm with progressive springs",
            }

    class Meta:
        ordering = ["-published_at", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(status="draft") | Q(published_at__isnull=False),
                name="published_post_requires_date",
            )
        ]


class Comment(models.Model):
    class Visibility(models.TextChoices):
        VISIBLE = "visible", _("Visible")
        WITHDRAWN = "withdrawn", _("Withdrawn by author")
        HIDDEN = "hidden", _("Hidden by moderator")

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    visibility = models.CharField(
        max_length=10, choices=Visibility.choices, default=Visibility.VISIBLE
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_comments",
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    def clean(self):
        if self.parent:
            if self.parent.post_id != self.post_id:
                raise ValidationError(
                    {"parent": _("Replies must belong to the same post.")}
                )
            if self.parent.parent_id:
                raise ValidationError(
                    {"parent": _("Replies can only be one level deep.")}
                )

    @property
    def is_visible(self):
        return self.visibility == self.Visibility.VISIBLE

    class Meta:
        ordering = ["created_at"]
        permissions = [("moderate_comment", "Can moderate comments")]
