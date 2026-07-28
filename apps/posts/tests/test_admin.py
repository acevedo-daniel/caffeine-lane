from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.posts.models import Comment, Post
from apps.tests.factories import PostFactory, UserFactory


class EditorialAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = UserFactory(is_staff=True)
        cls.editor = UserFactory(is_staff=True, is_superuser=True)
        cls.post = PostFactory(author=cls.editor, status=Post.Status.DRAFT)
        cls.comment = Comment.objects.create(
            post=cls.post, author=cls.staff_user, content="Needs moderation"
        )

    def test_admin_requires_staff_access(self):
        visitor = UserFactory()
        self.client.force_login(visitor)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.staff_user)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)

    def test_post_actions_publish_and_unpublish_through_services(self):
        self.client.force_login(self.editor)
        changelist_url = reverse("admin:posts_post_changelist")

        response = self.client.post(
            changelist_url,
            {"action": "publish_selected", "_selected_action": [self.post.pk]},
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, Post.Status.PUBLISHED)
        self.assertIsNotNone(self.post.published_at)

        self.client.post(
            changelist_url,
            {"action": "unpublish_selected", "_selected_action": [self.post.pk]},
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, Post.Status.DRAFT)
        self.assertIsNone(self.post.published_at)

    def test_moderation_action_needs_permission_and_hides_comment(self):
        permissions = Permission.objects.filter(
            codename__in=["change_comment", "moderate_comment"]
        )
        self.staff_user.user_permissions.add(*permissions)
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("admin:posts_comment_changelist"),
            {"action": "hide_selected_comments", "_selected_action": [self.comment.pk]},
        )

        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.visibility, Comment.Visibility.HIDDEN)
        self.assertEqual(self.comment.moderated_by, self.staff_user)
