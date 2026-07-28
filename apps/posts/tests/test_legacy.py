from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.posts.models import Comment, Post
from apps.posts.services import publish_post, unpublish_post
from apps.tests.factories import CategoryFactory, PostFactory, UserFactory


class PostEditorialDomainTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = UserFactory(username="author")
        cls.category = CategoryFactory(name="Builds")
        cls.post = PostFactory(
            title="Published Build", author=cls.author, categories=cls.category
        )

    def test_category_search_and_published_detail_render(self):
        self.assertEqual(
            self.client.get(
                reverse("category_view", kwargs={"category_slug": self.category.slug})
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("search"), {"q": "Published"}).status_code, 200
        )
        self.assertEqual(
            self.client.get(
                reverse("post_detail", kwargs={"slug": self.post.slug})
            ).status_code,
            200,
        )

    def test_draft_is_not_available_publicly(self):
        draft = Post.objects.create(
            title="Private draft", content="Draft content", author=self.author
        )

        self.assertEqual(
            self.client.get(
                reverse("post_detail", kwargs={"slug": draft.slug})
            ).status_code,
            404,
        )
        self.assertNotIn(draft, Post.objects.for_listing())

    def test_publish_requires_date_and_services_manage_it(self):
        post = Post.objects.create(
            title="Ready to publish", content="Content", author=self.author
        )
        post.status = Post.Status.PUBLISHED
        with self.assertRaises(ValidationError):
            post.full_clean()

        publish_post(post)
        post.refresh_from_db()
        self.assertEqual(post.status, Post.Status.PUBLISHED)
        self.assertIsNotNone(post.published_at)

        unpublish_post(post)
        post.refresh_from_db()
        self.assertEqual(post.status, Post.Status.DRAFT)
        self.assertIsNone(post.published_at)

    def test_slug_is_unique_and_stable_after_publication(self):
        first = Post.objects.create(
            title="Stable slug", content="Content", author=self.author
        )
        second = Post.objects.create(
            title="Stable slug", content="Content", author=self.author
        )
        publish_post(first, published_at=timezone.now())
        first.title = "Renamed after publication"
        first.save()

        self.assertEqual(first.slug, "stable-slug")
        self.assertEqual(second.slug, "stable-slug-2")

    def test_visible_image_requires_alt_text(self):
        post = Post(
            title="Accessible image",
            content="Content",
            author=self.author,
            featured_image="posts/media/example.jpg",
        )

        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_comment_requires_login_then_creates_comment(self):
        url = reverse("post_detail", kwargs={"slug": self.post.slug})
        anonymous = self.client.post(url, {"content": "Anonymous comment"})
        self.assertRedirects(anonymous, reverse("login"))

        self.client.force_login(self.author)
        response = self.client.post(url, {"content": "Authenticated comment"})
        self.assertRedirects(response, url)
        self.assertTrue(
            Comment.objects.filter(content="Authenticated comment").exists()
        )

    def test_post_creation_requires_permission(self):
        anonymous = self.client.get(reverse("post_create"))
        self.assertEqual(anonymous.status_code, 302)

        self.client.force_login(self.author)
        forbidden = self.client.get(reverse("post_create"))
        self.assertEqual(forbidden.status_code, 403)

        self.author.user_permissions.add(Permission.objects.get(codename="add_post"))
        self.assertEqual(self.client.get(reverse("post_create")).status_code, 200)
