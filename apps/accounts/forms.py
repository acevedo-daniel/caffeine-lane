from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class EmailRegistrationForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Your email address"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with that email already exists. Please choose a different one."
            )
        return email


class RegistrationStep2Form(UserCreationForm):
    gender = forms.ChoiceField(
        choices=Profile.GENDER_CHOICES,
        required=False,
        widget=forms.RadioSelect,
        label="What is your gender?",
    )
    has_moto = forms.ChoiceField(
        choices=[("True", "Yes"), ("False", "No")],
        required=True,
        widget=forms.RadioSelect,
        label="Own a motorcycle?",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name")

    def save(self, commit=True, email=None):
        user = super().save(commit=False)
        if email:
            user.email = email

        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.gender = self.cleaned_data.get("gender")
            profile.has_moto = self.cleaned_data.get("has_moto") == "True"
            profile.save()
        return user


class ProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=Profile.GENDER_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="What is your gender?",
    )
    has_moto = forms.ChoiceField(
        choices=[(True, "Yes"), (False, "No")],
        widget=forms.RadioSelect,
        label="Do you own a motorcycle?",
    )

    class Meta:
        model = Profile
        fields = ["bio", "avatar", "personal_url", "birth_date", "gender", "has_moto"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 3}),
        }
