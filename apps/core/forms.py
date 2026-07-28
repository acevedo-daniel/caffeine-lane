from django import forms


class ContactForm(forms.Form):
    from_name = forms.CharField(
        label="Your Name",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "Tell us who you are",
            }
        ),
    )

    from_email = forms.EmailField(
        label="Your Email",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "So we can reply to you",
            }
        ),
    )

    subject = forms.CharField(
        label="Subject",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "What is your message about?",
            }
        ),
    )

    message = forms.CharField(
        label="Your Message",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "Write your message here...",
                "rows": 5,
            }
        ),
    )
