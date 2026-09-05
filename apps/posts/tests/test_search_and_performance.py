from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
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

    def test_search_filters_are_available_without_javascript(self):
        response = self.client.get(reverse("search"))

        self.assertContains(
            response, 'id="filter-section" class="search-panel__filters"'
        )
        self.assertNotContains(response, "search-panel__filters hidden")

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

    def test_search_supports_multi_category_and_slug_filtering(self):
        reviews = CategoryFactory(name="Reviews")
        review_post = PostFactory(
            title="Helmet Review",
            author=self.author,
            categories=reviews,
        )

        # Test single category by slug
        response_slug = self.client.get(reverse("search"), {"category": "reviews"})
        self.assertContains(response_slug, review_post.title)
        self.assertNotContains(response_slug, self.related.title)

        # Test multi-category filtering
        response_multi = self.client.get(
            reverse("search"),
            {"category": [self.builds.slug, reviews.slug]},
        )
        self.assertContains(response_multi, self.related.title)
        self.assertContains(response_multi, review_post.title)
        self.assertNotContains(response_multi, self.match.title)

    def test_zero_results_renders_rider_empty_state_and_suggested_topic_pills(self):
        response = self.client.get(reverse("search"), {"q": "nonexistenttermxyz"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "search-empty-card")
        self.assertContains(response, "character-searching.webp")
        self.assertContains(response, "CB750")
        self.assertContains(response, "BMW R-Series")
        self.assertContains(response, "Carb Tuning")
        self.assertContains(response, "Cafe Seat Guide")

    def test_search_highlighting_template_filter(self):
        from apps.posts.templatetags.post_i18n import highlight_search

        text = "This is a great cafe racer build with custom exhaust."
        result = highlight_search(text, "cafe exhaust")
        self.assertIn('<mark class="search-highlight">cafe</mark>', result)
        self.assertIn('<mark class="search-highlight">exhaust</mark>', result)

        # Test XSS safety
        unsafe = "<script>alert('xss')</script> cafe"
        safe_result = highlight_search(unsafe, "cafe")
        self.assertNotIn("<script>", safe_result)
        self.assertIn("&lt;script&gt;", safe_result)
        self.assertIn('<mark class="search-highlight">cafe</mark>', safe_result)

    def test_search_ranking_prioritizes_title_over_content_in_postgresql(self):
        from django.db import connection

        title_match = PostFactory(
            title="Custom Mikuni setup",
            excerpt="General workshop update",
            content="Standard chassis assembly notes",
            author=self.author,
            categories=self.builds,
        )
        content_match = PostFactory(
            title="General assembly",
            excerpt="Regular garage notes",
            content="Detailed installation of a Mikuni carburetor for the build",
            author=self.author,
            categories=self.builds,
        )

        response = self.client.get(reverse("search"), {"q": "Mikuni"})
        results = list(response.context["results"])
        self.assertIn(title_match, results)
        self.assertIn(content_match, results)

        if connection.vendor == "postgresql":
            # Title match (weight A) must rank ahead of content match (weight C)
            self.assertEqual(results[0], title_match)

    def test_draft_preview_in_post_detail_by_role(self):
        draft = Post.objects.create(
            title="Secret Draft",
            slug="secret-draft",
            content="Draft notes",
            author=self.author,
            status=Post.Status.DRAFT,
        )
        editor = UserFactory(username="editor")
        editor.user_permissions.add(Permission.objects.get(codename="change_post"))
        stranger = UserFactory(username="stranger")

        url = reverse("post_detail", kwargs={"slug": draft.slug})

        # Anonymous gets 404
        self.assertEqual(self.client.get(url).status_code, 404)

        # Stranger gets 404
        self.client.force_login(stranger)
        self.assertEqual(self.client.get(url).status_code, 404)

        # Author can view draft
        self.client.force_login(self.author)
        self.assertEqual(self.client.get(url).status_code, 200)

        # Editor can view draft
        self.client.force_login(editor)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_post_cbv_success_messages_and_permissions(self):
        author = self.author
        author.user_permissions.add(
            Permission.objects.get(codename="add_post"),
            Permission.objects.get(codename="change_post"),
            Permission.objects.get(codename="delete_post"),
        )
        self.client.force_login(author)

        # Create
        create_res = self.client.post(
            reverse("post_create"),
            {
                "title": "Fresh Post",
                "excerpt": "Fresh excerpt",
                "content": "Fresh body",
                "categories": [self.builds.pk],
                "status": Post.Status.PUBLISHED,
                "published_at": "2026-09-05 12:00:00",
            },
            follow=True,
        )
        self.assertEqual(create_res.status_code, 200)
        messages = list(get_messages(create_res.wsgi_request))
        self.assertTrue(any("created successfully" in str(m) for m in messages))

        created_post = Post.objects.get(title="Fresh Post")
        self.assertEqual(created_post.author, author)

        # Update
        update_res = self.client.post(
            reverse("post_update", kwargs={"slug": created_post.slug}),
            {
                "title": "Fresh Post Edited",
                "excerpt": "Fresh excerpt",
                "content": "Fresh body",
                "categories": [self.builds.pk],
                "status": Post.Status.PUBLISHED,
                "published_at": "2026-09-05 12:00:00",
            },
            follow=True,
        )
        self.assertEqual(update_res.status_code, 200)
        messages = list(get_messages(update_res.wsgi_request))
        self.assertTrue(any("updated successfully" in str(m) for m in messages))

        # Other user cannot update author's post
        stranger = UserFactory(username="other-author")
        stranger.user_permissions.add(
            Permission.objects.get(codename="change_post"),
            Permission.objects.get(codename="delete_post"),
        )
        self.client.force_login(stranger)
        unauth_update = self.client.get(
            reverse("post_update", kwargs={"slug": created_post.slug})
        )
        self.assertEqual(unauth_update.status_code, 404)

        # Delete by author
        self.client.force_login(author)
        delete_res = self.client.post(
            reverse("post_delete", kwargs={"slug": created_post.slug}),
            follow=True,
        )
        self.assertEqual(delete_res.status_code, 200)
        messages = list(get_messages(delete_res.wsgi_request))
        self.assertTrue(any("deleted successfully" in str(m) for m in messages))
        self.assertFalse(Post.objects.filter(pk=created_post.pk).exists())
