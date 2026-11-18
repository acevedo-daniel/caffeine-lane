from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    from_name = forms.CharField(
        label=_("Your name"),
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("What should we call you?"),
            }
        ),
    )

    from_email = forms.EmailField(
        label=_("Your email address"),
        required=True,
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "placeholder": _("So we can reply"),
            }
        ),
    )

    subject = forms.CharField(
        label=_("Subject"),
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("What is your message about?"),
            }
        ),
    )

    message = forms.CharField(
        label=_("Your message"),
        required=True,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "placeholder": _("Write your message..."),
                "rows": 5,
            }
        ),
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError(_("Spam detected."))
        return ""
