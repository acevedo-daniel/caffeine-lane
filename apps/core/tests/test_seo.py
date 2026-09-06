from django.test import TestCase, override_settings
from django.urls import reverse

from apps.tests.factories import PostFactory


class PublicMetadataTests(TestCase):
    def test_public_home_has_social_metadata_and_website_schema(self):
        PostFactory()

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="robots" content="index, follow"')
        self.assertContains(response, 'rel="canonical" href="http://testserver/home/"')
        self.assertContains(response, 'property="og:type" content="website"')
        self.assertContains(
            response, 'name="twitter:card" content="summary_large_image"'
        )
        self.assertContains(response, 'type="application/ld+json"')
        self.assertContains(response, '"@type": "WebSite"')
        self.assertContains(response, "images/favicon.svg")
        self.assertContains(response, "images/site.webmanifest")

    def test_article_metadata_has_article_schema(self):
        post = PostFactory(title="Honda CB550 de ruta")

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'property="og:type" content="article"')
        self.assertContains(response, '"@type": "Article"')
        self.assertContains(response, post.title)

    def test_private_and_dynamic_surfaces_are_noindex(self):
        PostFactory(title="Cafe Racer en el taller")

        for url, robots in (
            (reverse("login"), "noindex, nofollow"),
            (reverse("search"), "noindex, follow"),
            (reverse("contact"), "noindex, follow"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, f'name="robots" content="{robots}"')

        response = self.client.get(f"{reverse('search')}?q=cafe")
        self.assertContains(response, 'name="robots" content="noindex, follow"')
        self.assertContains(
            response, 'rel="canonical" href="http://testserver/posts/search/"'
        )

    def test_robots_and_sitemap_expose_public_urls(self):
        post = PostFactory(title="CB750 en el taller")

        robots = self.client.get(reverse("robots_txt"))
        sitemap = self.client.get(reverse("sitemap"))

        self.assertEqual(robots.status_code, 200)
        self.assertEqual(robots["Content-Type"], "text/plain")
        self.assertContains(robots, "Sitemap: http://testserver/sitemap.xml")
        self.assertContains(robots, "Disallow: /accounts/")
        self.assertContains(robots, "Disallow: /posts/search/")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, post.get_absolute_url())
        self.assertNotContains(sitemap, "/accounts/")
        self.assertNotContains(sitemap, "/posts/search/")

    @override_settings(PUBLIC_SITE_URL="https://caffeine-lane.vercel.app/")
    def test_configured_public_site_url_is_used_for_public_metadata(self):
        response = self.client.get(reverse("home"))
        robots = self.client.get(reverse("robots_txt"))

        self.assertContains(
            response,
            'rel="canonical" href="https://caffeine-lane.vercel.app/home/"',
        )
        self.assertContains(
            robots, "Sitemap: https://caffeine-lane.vercel.app/sitemap.xml"
        )
