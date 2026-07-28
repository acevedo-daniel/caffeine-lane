from django.contrib import admin

from .models import Category, Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "published_at", "created_at"]
    list_filter = ["status", "published_at", "categories"]
    search_fields = ["title", "excerpt", "content"]
    readonly_fields = ["slug", "created_at", "updated_at"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "visibility", "created_at", "is_edited"]
    list_filter = ["visibility", "created_at"]
    search_fields = ["content", "author__username"]
