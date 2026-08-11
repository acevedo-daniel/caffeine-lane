from django import forms


class ContactForm(forms.Form):
    from_name = forms.CharField(
        label="Your name",
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "What should we call you?",
            }
        ),
    )

    from_email = forms.EmailField(
        label="Your email address",
        required=True,
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "So we can reply",
            }
        ),
    )

    subject = forms.CharField(
        label="Subject",
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "What is your message about?",
            }
        ),
    )

    message = forms.CharField(
        label="Your message",
        required=True,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "Write your message...",
                "rows": 5,
            }
        ),
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError("Spam detected.")
        return ""
