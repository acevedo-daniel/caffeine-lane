from html.parser import HTMLParser

from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.posts.models import Category, Post


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


@override_settings(DEBUG=False)
class NavigationContractTests(TestCase):
    def setUp(self):
        call_command("seed_demo")

    def test_seed_demo_creates_the_complete_structural_taxonomy(self):
        self.assertSetEqual(
            set(Category.objects.values_list("slug", flat=True)),
            {"builds", "guides", "reviews"},
        )
        self.assertEqual(Post.objects.count(), 3)

    def test_global_navigation_links_never_return_an_unexpected_error(self):
        response = self.client.get("/home/")
        self.assertEqual(response.status_code, 200)

        parser = LayoutNavigationParser()
        parser.feed(response.content.decode())
        self.assertTrue(parser.hrefs)

        for href in set(parser.hrefs):
            with self.subTest(href=href):
                linked_response = self.client.get(href)
                self.assertIn(linked_response.status_code, {200, 302, 403, 405})
