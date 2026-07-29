from django import forms


class ContactForm(forms.Form):
    from_name = forms.CharField(
        label="Tu nombre",
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "¿Cómo te llamás?",
            }
        ),
    )

    from_email = forms.EmailField(
        label="Tu correo electrónico",
        required=True,
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "Para poder responderte",
            }
        ),
    )

    subject = forms.CharField(
        label="Asunto",
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "¿De qué se trata tu mensaje?",
            }
        ),
    )

    message = forms.CharField(
        label="Tu mensaje",
        required=True,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent",
                "placeholder": "Escribí tu mensaje...",
                "rows": 5,
            }
        ),
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError("Spam detected.")
        return ""
