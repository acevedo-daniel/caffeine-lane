from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Post


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return ["landing", "home", "about"]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Category.objects.all()

    def location(self, item):
        return reverse("category_view", kwargs={"category_slug": item.slug})


class PostSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return Post.objects.published()

    def lastmod(self, item):
        return item.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "categories": CategorySitemap,
    "posts": PostSitemap,
}
