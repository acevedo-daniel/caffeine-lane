from html.parser import HTMLParser

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.posts.models import Category


class LayoutNavigationParser(HTMLParser):
    layout_sections = {"header", "footer"}

    def __init__(self):
        super().__init__()
        self._section_depth = 0
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag in self.layout_sections:
            self._section_depth += 1
        if tag == "a" and self._section_depth:
            href = dict(attrs).get("href")
            if href and href.startswith("/"):
                self.hrefs.append(href)

    def handle_endtag(self, tag):
        if tag in self.layout_sections:
            self._section_depth -= 1


class InternalLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href and href.startswith("/") and not href.startswith("//"):
            self.hrefs.append(href)


@override_settings(DEBUG=False)
class NavigationContractTests(TestCase):
    def test_fresh_database_has_the_complete_structural_taxonomy(self):
        self.assertSetEqual(
            set(Category.objects.values_list("slug", flat=True)),
            {"builds", "guides", "reviews"},
        )

    def test_all_documented_public_routes_render_on_a_fresh_database(self):
        routes = (
            "/",
            "/home/",
            "/about/",
            "/contact/",
            "/posts/search/",
            "/posts/category/builds/",
            "/posts/category/guides/",
            "/posts/category/reviews/",
            "/accounts/login/",
            "/accounts/register/",
            "/accounts/password-reset/",
        )

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_global_navigation_links_never_return_an_unexpected_error(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        parser = LayoutNavigationParser()
        parser.feed(response.content.decode())
        self.assertTrue(parser.hrefs)

        for href in set(parser.hrefs):
            with self.subTest(href=href):
                linked_response = self.client.get(href)
                self.assertIn(linked_response.status_code, {200, 302, 403, 405})

    def test_home_cards_and_layout_links_never_return_404_or_500(self):
        call_command("seed_portfolio")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        parser = InternalLinkParser()
        parser.feed(response.content.decode())
        self.assertTrue(parser.hrefs)

        for href in set(parser.hrefs):
            with self.subTest(href=href):
                linked_response = self.client.get(href)
                self.assertNotIn(linked_response.status_code, {404, 500})

    def test_landing_cards_and_layout_links_never_return_404_or_500(self):
        call_command("seed_portfolio")
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)

        parser = InternalLinkParser()
        parser.feed(response.content.decode())
        self.assertTrue(parser.hrefs)

        for href in set(parser.hrefs):
            with self.subTest(href=href):
                linked_response = self.client.get(href)
                self.assertNotIn(linked_response.status_code, {404, 500})
