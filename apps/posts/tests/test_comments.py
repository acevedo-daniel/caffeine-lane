from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.posts.models import Comment
from apps.tests.factories import PostFactory, UserFactory


class CommentModerationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = UserFactory(username="author")
        cls.other_user = UserFactory(username="other")
        cls.moderator = UserFactory(username="moderator")
        cls.moderator.user_permissions.add(
            Permission.objects.get(codename="moderate_comment")
        )
        cls.post = PostFactory(author=cls.author)
        cls.other_post = PostFactory(author=cls.author)

    def create_comment(self, *, author=None, content="A useful comment", parent=None):
        return Comment.objects.create(
            post=self.post, author=author or self.author, content=content, parent=parent
        )

    def test_reply_is_limited_to_one_level_and_same_post(self):
        root = self.create_comment()
        reply = self.create_comment(
            author=self.other_user, content="A reply", parent=root
        )

        nested = Comment(
            post=self.post, author=self.author, content="Nested reply", parent=reply
        )
        with self.assertRaises(ValidationError):
            nested.full_clean()

        wrong_post = Comment(
            post=self.other_post, author=self.author, content="Wrong post", parent=root
        )
        with self.assertRaises(ValidationError):
            wrong_post.full_clean()

    def test_reply_endpoint_creates_reply_and_rejects_nested_reply(self):
        root = self.create_comment()
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("comment_reply", kwargs={"comment_id": root.pk}),
            {"content": "A reply", "website": ""},
        )
        self.assertRedirects(response, root.post.get_absolute_url())
        reply = Comment.objects.get(parent=root)

        response = self.client.post(
            reverse("comment_reply", kwargs={"comment_id": reply.pk}),
            {"content": "Nested reply", "website": ""},
        )
        self.assertRedirects(response, root.post.get_absolute_url())
        self.assertEqual(Comment.objects.filter(parent=reply).count(), 0)

    def test_reply_composer_preserves_a_no_javascript_form_fallback(self):
        comment = self.create_comment()
        self.client.force_login(self.other_user)

        response = self.client.get(comment.post.get_absolute_url())

        self.assertContains(response, "data-reply-open")
        self.assertContains(response, "data-reply-form")
        self.assertContains(response, "data-reply-cancel")
        self.assertContains(response, reverse("comment_reply", args=[comment.pk]))
        self.assertNotContains(response, f'id="reply-form-{comment.pk}" hidden')

    def test_anonymous_visitors_do_not_receive_reply_composers(self):
        self.create_comment()

        response = self.client.get(self.post.get_absolute_url())

        self.assertNotContains(response, "data-reply-open")
        self.assertNotContains(response, "data-reply-form")

    def test_author_can_edit_and_withdraw_but_other_user_cannot(self):
        comment = self.create_comment()
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("comment_edit", kwargs={"comment_id": comment.pk}),
            {"content": "Edited comment", "website": ""},
        )
        self.assertRedirects(response, comment.post.get_absolute_url())
        comment.refresh_from_db()
        self.assertTrue(comment.is_edited)
        self.assertEqual(comment.content, "Edited comment")

        response = self.client.post(reverse("comment_withdraw", args=[comment.pk]))
        self.assertRedirects(response, comment.post.get_absolute_url())
        comment.refresh_from_db()
        self.assertEqual(comment.visibility, Comment.Visibility.WITHDRAWN)

        self.client.force_login(self.other_user)
        self.assertEqual(
            self.client.post(
                reverse("comment_withdraw", args=[comment.pk])
            ).status_code,
            403,
        )

    def test_moderator_hides_without_deleting_conversation(self):
        comment = self.create_comment()
        reply = self.create_comment(
            author=self.other_user, content="A reply", parent=comment
        )
        self.client.force_login(self.moderator)

        response = self.client.post(reverse("comment_hide", args=[comment.pk]))
        self.assertRedirects(response, comment.post.get_absolute_url())
        comment.refresh_from_db()
        self.assertEqual(comment.visibility, Comment.Visibility.HIDDEN)
        self.assertTrue(Comment.objects.filter(pk=reply.pk).exists())

        response = self.client.get(comment.post.get_absolute_url())
        self.assertContains(response, "hidden by moderation")
        self.assertContains(response, reply.content)
        self.assertNotContains(response, "data-reply-open")

    def test_moderator_can_edit_and_hidden_comments_cannot_receive_replies(self):
        comment = self.create_comment()
        self.client.force_login(self.moderator)
        response = self.client.post(
            reverse("comment_edit", args=[comment.pk]),
            {"content": "Moderator edit", "website": ""},
        )
        self.assertRedirects(response, comment.post.get_absolute_url())
        comment.refresh_from_db()
        self.assertEqual(comment.content, "Moderator edit")

        self.client.post(reverse("comment_hide", args=[comment.pk]))
        response = self.client.post(
            reverse("comment_reply", args=[comment.pk]),
            {"content": "Blocked reply", "website": ""},
        )
        self.assertRedirects(response, comment.post.get_absolute_url())
        self.assertFalse(Comment.objects.filter(content="Blocked reply").exists())

    def test_spam_honeypot_and_duplicate_comment_are_rejected(self):
        self.client.force_login(self.author)
        url = self.post.get_absolute_url()
        self.client.post(url, {"content": "Repeated comment", "website": ""})
        self.client.post(url, {"content": "Repeated comment", "website": ""})
        self.client.post(
            url, {"content": "Spam comment", "website": "https://spam.test"}
        )

        self.assertEqual(Comment.objects.filter(content="Repeated comment").count(), 1)
        self.assertFalse(Comment.objects.filter(content="Spam comment").exists())

    def test_destructive_actions_require_post_and_controls_follow_permissions(self):
        comment = self.create_comment()
        self.client.force_login(self.author)
        self.assertEqual(
            self.client.get(reverse("comment_withdraw", args=[comment.pk])).status_code,
            405,
        )
        self.assertEqual(
            self.client.get(reverse("comment_hide", args=[comment.pk])).status_code,
            405,
        )

        self.client.force_login(self.other_user)
        response = self.client.get(comment.post.get_absolute_url())
        self.assertNotContains(response, reverse("comment_edit", args=[comment.pk]))
        self.assertNotContains(response, reverse("comment_withdraw", args=[comment.pk]))
        self.assertNotContains(response, reverse("comment_hide", args=[comment.pk]))
