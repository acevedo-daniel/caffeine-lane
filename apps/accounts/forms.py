from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class EmailRegistrationForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Your email address"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class RegistrationStep2Form(UserCreationForm):
    has_motorcycle = forms.TypedChoiceField(
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        widget=forms.RadioSelect,
        label="Own a motorcycle?",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "display_name", "has_motorcycle")

    def validate_registration_email(self, email):
        if User.objects.filter(email__iexact=email).exists():
            self.add_error(None, "An account with this email already exists.")
            return False
        return True

    def save(self, commit=True, *, email):
        user = super().save(commit=False)
        user.email = email
        user.has_motorcycle = self.cleaned_data["has_motorcycle"]
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["display_name", "bio", "avatar", "personal_url", "has_motorcycle"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "has_motorcycle": forms.CheckboxInput(),
        }
