from django import forms
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .models import Category, Comment, Post, is_reserved_post_slug
from .presentation import category_label

SORT_CHOICES = [
    ("relevance", _("Relevance")),
    ("newest", _("Newest")),
    ("oldest", _("Oldest")),
    ("title_asc", _("Title (A-Z)")),
    ("title_desc", _("Title (Z-A)")),
]


class LocalizedCategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, category):
        return category_label(category)


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
                    "placeholder": _("Write your comment here..."),
                }
            )
        }
        labels = {"content": _("Your comment")}

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content) < 3:
            raise forms.ValidationError(
                _("Comments must contain at least 3 characters.")
            )
        return content

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError(_("Spam detected."))
        return ""


class PostSearchForm(forms.Form):
    q = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full py-2 px-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black",
                "placeholder": _("Search posts..."),
            }
        ),
    )
    category = LocalizedCategoryChoiceField(
        label=_("Category"),
        queryset=Category.objects.all(),
        required=False,
        empty_label=_("All categories"),
        widget=forms.Select(
            attrs={
                "class": "w-full py-2 px-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black",
            }
        ),
    )
    sort = forms.ChoiceField(
        label=_("Sort by"),
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
        labels = {
            "title": _("Title"),
            "excerpt": _("Excerpt"),
            "content": _("Content"),
            "featured_image": _("Featured image"),
            "featured_image_alt": _("Featured image alternative text"),
            "categories": _("Categories"),
            "status": _("Status"),
            "published_at": _("Publication date"),
        }

    def clean(self):
        cleaned_data = super().clean()
        generated_slug = slugify(cleaned_data.get("title", ""))
        if generated_slug and is_reserved_post_slug(generated_slug):
            self.add_error(
                "title",
                _("This title would create a slug reserved for an application route."),
            )
        if cleaned_data.get("status") == Post.Status.PUBLISHED and not cleaned_data.get(
            "published_at"
        ):
            self.add_error("published_at", _("Published posts require a date."))
        if cleaned_data.get("featured_image") and not cleaned_data.get(
            "featured_image_alt"
        ):
            self.add_error(
                "featured_image_alt", _("Visible images require alternative text.")
            )
        return cleaned_data
