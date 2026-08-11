from django.utils import timezone

from .models import Post


def publish_post(post: Post, *, published_at=None) -> Post:
    post.status = Post.Status.PUBLISHED
    post.published_at = published_at or timezone.now()
    post.full_clean()
    post.save(update_fields=["status", "published_at", "updated_at"])
    return post


def unpublish_post(post: Post) -> Post:
    post.status = Post.Status.DRAFT
    post.published_at = None
    post.save(update_fields=["status", "published_at", "updated_at"])
    return post
