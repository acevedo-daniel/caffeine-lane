from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import Comment, Post


def create_comment(*, post: Post, author, content: str, parent=None) -> Comment:
    if parent and not parent.is_visible:
        raise ValidationError(_("Replies are only allowed on visible comments."))
    recent_duplicate = Comment.objects.filter(
        post=post,
        author=author,
        content=content,
        created_at__gte=timezone.now() - timedelta(minutes=1),
    ).exists()
    if recent_duplicate:
        raise ValidationError(
            _("Please wait before submitting the same comment again.")
        )

    comment = Comment(post=post, author=author, content=content, parent=parent)
    comment.full_clean()
    comment.save()
    return comment


def withdraw_comment(*, comment: Comment, actor) -> Comment:
    if comment.author_id != actor.pk:
        raise PermissionDenied
    comment.visibility = Comment.Visibility.WITHDRAWN
    comment.moderated_at = timezone.now()
    comment.moderated_by = actor
    comment.save(
        update_fields=["visibility", "moderated_at", "moderated_by", "updated_at"]
    )
    return comment


def hide_comment(*, comment: Comment, actor) -> Comment:
    if not actor.has_perm("posts.moderate_comment"):
        raise PermissionDenied
    comment.visibility = Comment.Visibility.HIDDEN
    comment.moderated_at = timezone.now()
    comment.moderated_by = actor
    comment.save(
        update_fields=["visibility", "moderated_at", "moderated_by", "updated_at"]
    )
    return comment
