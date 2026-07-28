import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from apps.posts.models import Category, Post

from .forms import ContactForm

logger = logging.getLogger(__name__)


@csrf_exempt
def csp_report(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        report = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    logger.warning("CSP violation report: %s", report)
    return HttpResponse(status=204)


def landing(request):
    return render(request, "core/landing.html")


def home(request):
    posts = Post.objects.for_listing()
    banner_posts = posts[:5]

    new_builds = posts.filter(categories__slug="builds")[:9]

    new_guides = posts.filter(categories__slug="guides")[:6]

    new_reviews = posts.filter(categories__slug="reviews")[:4]
    total_posts = posts.count()
    categories = Category.objects.all()

    context = {
        "banner_posts": banner_posts,
        "new_builds": new_builds,
        "new_guides": new_guides,
        "new_reviews": new_reviews,
        "total_posts": total_posts,
        "categories": categories,
    }

    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["from_name"]
            email = form.cleaned_data["from_email"]
            subject = form.cleaned_data["subject"]
            message_text = form.cleaned_data["message"]

            full_message = f"From: {name} <{email}>\n\n{message_text}"

            send_mail(
                subject=f"Contact from Blog: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_RECIPIENT_EMAIL],
            )

            messages.success(
                request, "Thank you for your message! We will get back to you soon."
            )
            return redirect("contact")
    else:
        form = ContactForm()
    context = {
        "form": form,
    }
    return render(request, "core/contact.html", context)
