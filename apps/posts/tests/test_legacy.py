from django.contrib.auth.models import Permission, User
from django.template import VariableDoesNotExist
from django.test import TestCase
from django.urls import reverse

from apps.posts.models import Comment, Post
from apps.tests.factories import CategoryFactory, PostFactory, UserFactory


class LegacyPostsCharacterizationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = UserFactory(username="author")
        cls.category = CategoryFactory(name="Builds")
        cls.post = PostFactory(
            title="Legacy Build", author=cls.author, category=cls.category
        )

    def test_category_search_and_detail_render(self):
        self.assertEqual(
            self.client.get(
                reverse("category_view", kwargs={"category_slug": self.category.slug})
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("search"), {"q": "Legacy"}).status_code, 200
        )
        self.assertEqual(
            self.client.get(
                reverse("post_detail", kwargs={"slug": self.post.slug})
            ).status_code,
            200,
        )

    def test_comment_requires_login_then_creates_comment(self):
        url = reverse("post_detail", kwargs={"slug": self.post.slug})
        anonymous = self.client.post(url, {"content": "Anonymous comment"})
        self.assertRedirects(anonymous, reverse("login"))

        self.client.force_login(self.author)
        response = self.client.post(url, {"content": "Authenticated comment"})
        self.assertRedirects(response, url)
        self.assertTrue(Comment.objects.filter(content="Authenticated comment").exists())

    def test_post_creation_requires_permission(self):
        anonymous = self.client.get(reverse("post_create"))
        self.assertEqual(anonymous.status_code, 302)

        self.client.force_login(self.author)
        forbidden = self.client.get(reverse("post_create"))
        self.assertEqual(forbidden.status_code, 403)

        self.author.user_permissions.add(Permission.objects.get(codename="add_post"))
        with self.assertRaises(VariableDoesNotExist):
            self.client.get(reverse("post_create"))


class LegacyPostSaveFailureCharacterizationTests(TestCase):
    def test_existing_post_save_raises_when_slug_is_already_present(self):
        author = UserFactory(username="save-author")
        post = Post.objects.create(
            title="Existing Post", content="Content", author=author, status="published"
        )
        with self.assertRaisesRegex(UnboundLocalError, "original_slug"):
            post.save()
