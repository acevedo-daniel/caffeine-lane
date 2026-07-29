from django.test import TestCase
from django.urls import reverse

from apps.posts.models import Post
from apps.tests.factories import CategoryFactory, PostFactory, UserFactory


class SearchAndListingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = UserFactory(username="listing-author")
        cls.builds = CategoryFactory(name="Builds")
        cls.guides = CategoryFactory(name="Guides")
        cls.related = PostFactory(
            title="Carburetor guide",
            excerpt="Carburetor tuning notes",
            content="Workshop instructions",
            author=cls.author,
            categories=cls.builds,
        )
        cls.related_build = PostFactory(
            title="Build companion",
            excerpt="A related build article",
            content="Related workshop instructions",
            author=cls.author,
            categories=cls.builds,
        )
        cls.match = PostFactory(
            title="Brake setup",
            excerpt="Safe braking for road riding",
            content="A complete braking guide",
            author=cls.author,
            categories=cls.guides,
        )

    def test_search_form_allows_category_only_filtering(self):
        response = self.client.get(reverse("search"), {"category": self.guides.pk})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.match.title)
        self.assertNotContains(response, self.related.title)

    def test_search_matches_title_excerpt_and_content(self):
        for term in ("Brake", "riding", "complete"):
            with self.subTest(term=term):
                response = self.client.get(reverse("search"), {"q": term})
                self.assertContains(response, self.match.title)

    def test_category_and_search_are_paginated(self):
        for number in range(13):
            PostFactory(
                title=f"Build listing {number}",
                author=self.author,
                categories=self.builds,
            )

        category_response = self.client.get(
            reverse("category_view", kwargs={"category_slug": self.builds.slug}),
            {"page": 2},
        )
        search_response = self.client.get(
            reverse("search"), {"q": "Build listing", "page": 2}
        )

        self.assertTrue(category_response.context["is_paginated"])
        self.assertEqual(category_response.context["page_obj"].number, 2)
        self.assertTrue(search_response.context["is_paginated"])
        self.assertEqual(search_response.context["page_obj"].number, 2)

    def test_search_pagination_urlencodes_query_parameters(self):
        for number in range(13):
            PostFactory(
                title=f"Build & + listing {number}",
                author=self.author,
                categories=self.builds,
            )

        response = self.client.get(reverse("search"), {"q": "Build & +"})

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(response.context["pagination_query"], "q=Build+%26+%2B")
        self.assertContains(response, "?q=Build+%26+%2B&amp;page=2")

    def test_related_posts_share_categories(self):
        response = self.client.get(self.related.get_absolute_url())

        related_posts = list(response.context["related_posts"])
        self.assertIn(self.related_build, related_posts)
        self.assertNotIn(self.related, related_posts)
        self.assertNotIn(self.match, related_posts)

    def test_listing_queryset_uses_two_queries_for_author_and_categories(self):
        with self.assertNumQueries(2):
            posts = list(Post.objects.for_listing())
            for post in posts:
                str(post.author)
                list(post.categories.all())
