from django.contrib import admin
from django.utils.html import format_html

from .comment_services import hide_comment
from .models import Category, Comment, Post
from .services import publish_post, unpublish_post


def image_thumbnail(image, description):
    if not image:
        return "—"
    return format_html(
        '<img src="{}" alt="{}" width="48" height="48" />',
        image.url,
        description,
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "thumbnail",
        "author",
        "status",
        "published_at",
        "updated_at",
    ]
    list_filter = ["status", "categories", "published_at", "created_at"]
    search_fields = ["title", "excerpt", "content", "author__email", "author__username"]
    autocomplete_fields = ["author", "categories"]
    readonly_fields = ["slug", "created_at", "updated_at", "thumbnail"]
    list_select_related = ["author"]
    date_hierarchy = "published_at"
    ordering = ["-published_at", "-created_at"]
    actions = ["publish_selected", "unpublish_selected"]
    fieldsets = [
        ("Content", {"fields": ("title", "slug", "excerpt", "content")}),
        ("Media", {"fields": ("featured_image", "featured_image_alt", "thumbnail")}),
        ("Publication", {"fields": ("author", "categories", "status", "published_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    ]

    @admin.display(description="Image")
    def thumbnail(self, post):
        return image_thumbnail(post.featured_image, post.featured_image_alt)

    @admin.action(description="Publish selected posts")
    def publish_selected(self, request, queryset):
        for post in queryset:
            publish_post(post)

    @admin.action(description="Unpublish selected posts")
    def unpublish_selected(self, request, queryset):
        for post in queryset:
            unpublish_post(post)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "thumbnail", "created_at", "updated_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["slug", "created_at", "updated_at", "thumbnail"]
    ordering = ["name"]

    @admin.display(description="Image")
    def thumbnail(self, category):
        return image_thumbnail(category.image, category.name)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "post",
        "parent",
        "visibility",
        "is_edited",
        "moderated_by",
        "created_at",
    ]
    list_filter = ["visibility", "is_edited", "created_at", "moderated_at"]
    search_fields = [
        "content",
        "author__username",
        "author__email",
        "post__title",
    ]
    autocomplete_fields = ["post", "author", "parent", "moderated_by"]
    readonly_fields = ["created_at", "updated_at", "moderated_at", "moderated_by"]
    list_select_related = ["author", "post", "parent", "moderated_by"]
    date_hierarchy = "created_at"
    actions = ["hide_selected_comments"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm("posts.moderate_comment"):
            actions.pop("hide_selected_comments", None)
        return actions

    @admin.action(description="Hide selected comments")
    def hide_selected_comments(self, request, queryset):
        for comment in queryset.exclude(visibility=Comment.Visibility.HIDDEN):
            hide_comment(comment=comment, actor=request.user)
