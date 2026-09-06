import json
import logging

from anymail.exceptions import AnymailAPIError
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from apps.posts.models import Category, Post
from apps.posts.taxonomy import CategorySlug

from .forms import ContactForm
from .seo import absolute_url, article_schema, localized_copy, website_schema

logger = logging.getLogger(__name__)


@csrf_exempt
def csp_report(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if len(request.body) > 65536:
        return HttpResponse(status=400)
    try:
        report = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    logger.warning("CSP violation report: %s", report)
    return HttpResponse(status=204)


def health(request):
    return JsonResponse({"status": "ok"})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /csp-report/",
        "Disallow: /posts/comments/",
        "Disallow: /posts/new/",
        "Disallow: /posts/search/",
        "Disallow: /400/",
        "Disallow: /403/",
        "Disallow: /404/",
        "Disallow: /500/",
        f"Sitemap: {absolute_url(request, reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def landing(request):
    featured_build = (
        Post.objects.for_listing().filter(categories__slug=CategorySlug.BUILDS).first()
        or Post.objects.for_listing().first()
    )
    recent_posts = Post.objects.for_listing()[:3]
    categories = Category.objects.all()
    context = {
        "featured_build": featured_build,
        "recent_posts": recent_posts,
        "categories": categories,
        "builds_category_slug": CategorySlug.BUILDS,
        "guides_category_slug": CategorySlug.GUIDES,
        "reviews_category_slug": CategorySlug.REVIEWS,
        "seo_page_title": localized_copy(
            request,
            "Caffeine Lane · Cultura cafe racer curada",
            "Caffeine Lane · Curated Cafe Racer Culture",
        ),
        "seo_page_description": localized_copy(
            request,
            "Historias de taller, despieces técnicos y cultura cafe racer para "
            "quienes eligen el camino largo a casa.",
            "Workshop stories, technical breakdowns, and cafe racer culture for "
            "riders who choose the long way home.",
        ),
        "seo_page_image": (
            request.build_absolute_uri(featured_build.featured_image.url)
            if featured_build and featured_build.featured_image
            else None
        ),
        "seo_structured_data": website_schema(request),
    }
    return render(request, "core/landing.html", context)


def home(request):
    posts = Post.objects.for_listing()
    banner_posts = posts[:5]

    new_builds = posts.filter(categories__slug=CategorySlug.BUILDS)[:9]

    new_guides = posts.filter(categories__slug=CategorySlug.GUIDES)[:6]

    new_reviews = posts.filter(categories__slug=CategorySlug.REVIEWS)[:4]
    total_posts = posts.count()
    categories = Category.objects.all()

    context = {
        "banner_posts": banner_posts,
        "new_builds": new_builds,
        "new_guides": new_guides,
        "new_reviews": new_reviews,
        "builds_category_slug": CategorySlug.BUILDS,
        "guides_category_slug": CategorySlug.GUIDES,
        "reviews_category_slug": CategorySlug.REVIEWS,
        "total_posts": total_posts,
        "categories": categories,
        "seo_page_title": localized_copy(
            request,
            "Caffeine Lane · Inicio editorial",
            "Caffeine Lane · Editorial Home",
        ),
        "seo_page_description": localized_copy(
            request,
            "Explorá proyectos, guías y reseñas de motocicletas construidas para "
            "el taller y la ruta.",
            "Explore motorcycle builds, workshop guides, and reviews made for the "
            "garage and the open road.",
        ),
        "seo_page_image": (
            request.build_absolute_uri(banner_posts[0].featured_image.url)
            if banner_posts and banner_posts[0].featured_image
            else None
        ),
        "seo_structured_data": website_schema(request),
    }

    return render(request, "core/home.html", context)


def about(request):
    return render(
        request,
        "core/about.html",
        {
            "guides_category_slug": CategorySlug.GUIDES,
            "seo_page_title": localized_copy(
                request,
                "Acerca de Caffeine Lane · Cultura moto editorial",
                "About Caffeine Lane · Editorial Moto Culture",
            ),
            "seo_page_description": localized_copy(
                request,
                "Conocé el enfoque editorial de Caffeine Lane: oficio de garaje, "
                "criterio técnico y cultura motociclista.",
                "Learn about Caffeine Lane's editorial approach to garage craft, "
                "technical judgment, and motorcycle culture.",
            ),
        },
    )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            client_ip = (
                forwarded_for.split(",")[0].strip()
                if forwarded_for
                else request.META.get("REMOTE_ADDR", "")
            )
            rate_limit_key = f"contact-rate-limit:{client_ip}"
            if not cache.add(
                rate_limit_key, 1, timeout=settings.CONTACT_RATE_LIMIT_WINDOW
            ):
                cache.incr(rate_limit_key)
            if cache.get(rate_limit_key, 0) > settings.CONTACT_RATE_LIMIT:
                form.add_error(None, _("Too many messages. Please try again later."))
                return render(request, "core/contact.html", {"form": form})

            name = form.cleaned_data["from_name"]
            email = form.cleaned_data["from_email"]
            subject = form.cleaned_data["subject"]
            message_text = form.cleaned_data["message"]

            full_message = f"From: {name} <{email}>\n\n{message_text}"
            html_message = render_to_string(
                "core/contact_email.html",
                {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message_text,
                },
                request=request,
            )
            message = EmailMultiAlternatives(
                subject=_("Contact from Caffeine Lane: %(subject)s")
                % {"subject": subject},
                body=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECIPIENT_EMAIL],
                reply_to=[email],
            )
            message.attach_alternative(html_message, "text/html")
            try:
                message.send()
            except (AnymailAPIError, OSError) as error:
                logger.warning(
                    "Contact email delivery failed (backend=%s, error_type=%s)",
                    settings.EMAIL_BACKEND,
                    type(error).__name__,
                )
                messages.error(
                    request,
                    _(
                        "We could not send your message right now. Please try again later."
                    ),
                )
                return render(request, "core/contact.html", {"form": form}, status=503)

            messages.success(request, _("Message sent. We'll get back to you soon."))
            return redirect("contact")
    else:
        form = ContactForm()
    context = {
        "form": form,
        "seo_page_title": localized_copy(
            request, "Contacto · Caffeine Lane", "Contact Caffeine Lane"
        ),
        "seo_page_description": localized_copy(
            request,
            "Contactá al equipo editorial de Caffeine Lane.",
            "Contact the Caffeine Lane editorial team.",
        ),
        "seo_robots": "noindex, follow",
    }
    return render(request, "core/contact.html", context)
