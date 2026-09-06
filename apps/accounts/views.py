from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import EmailRegistrationForm, ProfileForm, RegistrationStep2Form


def password_reset(request):
    if not settings.PASSWORD_RESET_ENABLED:
        return render(request, "accounts/password_reset_unavailable.html")

    return auth_views.PasswordResetView.as_view(
        template_name="accounts/password_reset.html",
        email_template_name="accounts/password_reset_email.txt",
        html_email_template_name="accounts/password_reset_email.html",
        subject_template_name="accounts/password_reset_subject.txt",
    )(request)


def register_step1(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = EmailRegistrationForm(request.POST)
        if form.is_valid():
            request.session["registration_email"] = form.cleaned_data["email"]
            return redirect("register_step2")
    else:
        form = EmailRegistrationForm()

    return render(request, "accounts/register_step1.html", {"form": form})


def register_step2(request):
    if request.user.is_authenticated:
        return redirect("home")

    email = request.session.get("registration_email")
    if not email:
        return redirect("register_step1")

    if request.method == "POST":
        form = RegistrationStep2Form(request.POST, request.FILES)
        if form.is_valid() and form.validate_registration_email(email):
            try:
                with transaction.atomic():
                    user = form.save(email=email)
            except IntegrityError:
                form.add_error(
                    None,
                    _(
                        "This email cannot be registered. Please sign in or use another email address."
                    ),
                )
            else:
                login(request, user)
                del request.session["registration_email"]
                messages.success(request, _("Account created."))
                messages.info(
                    request,
                    _("Welcome — head to your profile to add your details."),
                )
                return redirect("home")
    else:
        form = RegistrationStep2Form()

    return render(request, "accounts/register_step2.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated."))
            return redirect("profile")
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = ProfileForm(instance=request.user)

    recent_comments = request.user.comments.select_related("post").order_by(
        "-created_at"
    )[:5]

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "recent_comments": recent_comments,
        },
    )


@require_POST
def custom_logout(request):
    logout(request)
    messages.success(request, _("You've been signed out."))
    return redirect("home")
