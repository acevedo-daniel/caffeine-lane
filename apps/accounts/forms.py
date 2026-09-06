from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class EmailRegistrationForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label=_("Email address"),
        widget=forms.EmailInput(attrs={"placeholder": _("you@example.com")}),
    )

    def clean_email(self):
        return self.cleaned_data["email"].lower()


class RegistrationStep2Form(UserCreationForm):
    has_motorcycle = forms.TypedChoiceField(
        choices=[("true", _("Yes")), ("false", _("No"))],
        coerce=lambda value: value == "true",
        widget=forms.RadioSelect,
        label=_("Do you ride a motorcycle?"),
    )
    avatar = forms.ImageField(
        required=False,
        label=_("Profile picture (optional)"),
        widget=forms.FileInput(
            attrs={
                "accept": "image/png,image/jpeg,image/webp",
                "data-avatar-input": "true",
                "id": "id_avatar",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "display_name", "has_motorcycle", "avatar")

    def validate_registration_email(self, email):
        if User.objects.filter(email__iexact=email).exists():
            self.add_error(
                None,
                _(
                    "This email cannot be registered. Please sign in or use another email address."
                ),
            )
            return False
        return True

    def save(self, commit=True, *, email):
        user = super().save(commit=False)
        user.email = email
        user.has_motorcycle = self.cleaned_data["has_motorcycle"]
        if self.cleaned_data.get("avatar"):
            user.avatar = self.cleaned_data["avatar"]
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["display_name", "bio", "avatar", "personal_url", "has_motorcycle"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "has_motorcycle": forms.CheckboxInput(),
            "avatar": forms.FileInput(
                attrs={
                    "accept": "image/png,image/jpeg,image/webp",
                    "data-avatar-input": "true",
                    "id": "id_profile_avatar",
                }
            ),
        }
