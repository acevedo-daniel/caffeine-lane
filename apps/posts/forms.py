from django import forms
from django.utils.text import slugify

from .models import Category, Comment, Post, is_reserved_post_slug

SORT_CHOICES = [
    ("relevance", "Relevance"),
    ("newest", "Newest"),
    ("oldest", "Oldest"),
    ("title_asc", "Title (A-Z)"),
    ("title_desc", "Title (Z-A)"),
]


class CommentForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "rows": 4,
                    "placeholder": "Write your comment here...",
                }
            )
        }
        labels = {"content": "Your Comment"}

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content) < 3:
            raise forms.ValidationError("Comments must contain at least 3 characters.")
        return content

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError("Spam detected.")
        return ""


class PostSearchForm(forms.Form):
    q = forms.CharField(
        label="Search",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full py-2 px-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black",
                "placeholder": "Search posts...",
            }
        ),
    )
    category = forms.ModelChoiceField(
        label="Category",
        queryset=Category.objects.all(),
        required=False,
        empty_label="All categories",
        widget=forms.Select(
            attrs={
                "class": "w-full py-2 px-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black",
            }
        ),
    )
    sort = forms.ChoiceField(
        label="Sort by",
        choices=SORT_CHOICES,
        required=False,
        initial="relevance",
        widget=forms.Select(
            attrs={
                "class": "w-full py-2 px-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black",
            }
        ),
    )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "excerpt",
            "content",
            "featured_image",
            "featured_image_alt",
            "categories",
            "status",
            "published_at",
        ]

    def clean(self):
        cleaned_data = super().clean()
        generated_slug = slugify(cleaned_data.get("title", ""))
        if generated_slug and is_reserved_post_slug(generated_slug):
            self.add_error(
                "title",
                "This title would create a slug reserved for an application route.",
            )
        if cleaned_data.get("status") == Post.Status.PUBLISHED and not cleaned_data.get(
            "published_at"
        ):
            self.add_error("published_at", "Published posts require a date.")
        if cleaned_data.get("featured_image") and not cleaned_data.get(
            "featured_image_alt"
        ):
            self.add_error(
                "featured_image_alt", "Visible images require alternative text."
            )
        return cleaned_data
