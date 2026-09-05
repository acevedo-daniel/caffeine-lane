from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .comment_services import (
    create_comment,
    hide_comment,
    update_comment,
    withdraw_comment,
)
from .forms import CommentForm, PostForm, PostSearchForm
from .models import Category, Comment, Post


def post_detail(request, slug):
    post_qs = Post.objects.with_author().with_categories()
    if request.user.is_authenticated and (
        request.user.is_staff or request.user.has_perm("posts.change_post")
    ):
        post = get_object_or_404(post_qs, slug=slug)
    elif request.user.is_authenticated:
        post = get_object_or_404(
            post_qs.filter(
                Q(status=Post.Status.PUBLISHED, published_at__isnull=False)
                | Q(author=request.user)
            ),
            slug=slug,
        )
    else:
        post = get_object_or_404(post_qs.published(), slug=slug)
    comments = (
        post.comments.filter(parent=None)
        .select_related("author")
        .prefetch_related(
            Prefetch("replies", queryset=Comment.objects.select_related("author"))
        )
    )
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, _("You must be logged in to comment."))
            return redirect("login")

        if form.is_valid():
            try:
                create_comment(
                    post=post,
                    author=request.user,
                    content=form.cleaned_data["content"],
                )
            except ValidationError as error:
                form.add_error("content", error)
                messages.error(request, _("Please correct the errors below."))
            else:
                messages.success(request, _("Comment posted."))
                return redirect("post_detail", slug=post.slug)

        else:
            messages.error(
                request,
                _("There was an error with your comment. Please try again."),
            )
    context = {
        "post": post,
        "comments": comments,
        "form": form,
        "related_posts": (
            Post.objects.for_listing()
            .filter(categories__in=post.categories.all())
            .exclude(pk=post.pk)
            .distinct()[:3]
        ),
    }
    return render(request, "posts/post_detail.html", context)


@login_required
@require_POST
def comment_reply(request, comment_id):
    parent = get_object_or_404(Comment.objects.select_related("post"), pk=comment_id)
    post = get_object_or_404(Post.objects.published(), pk=parent.post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        try:
            create_comment(
                post=post,
                author=request.user,
                content=form.cleaned_data["content"],
                parent=parent,
            )
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
        else:
            messages.success(request, _("Reply posted."))
    else:
        messages.error(request, _("Please correct the reply before submitting."))
    return redirect("post_detail", slug=post.slug)


def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    sort = request.GET.get("sort", "newest")
    posts_qs = Post.objects.for_listing().filter(categories=category)

    if sort == "oldest":
        posts_qs = posts_qs.order_by("published_at", "created_at")
    elif sort == "comments":
        posts_qs = posts_qs.annotate(
            comment_count=Count(
                "comments", filter=Q(comments__visibility=Comment.Visibility.VISIBLE)
            )
        ).order_by("-comment_count", "-published_at")
    else:
        sort = "newest"
        posts_qs = posts_qs.order_by("-published_at", "-created_at")

    paginator = Paginator(posts_qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    pagination_query = request.GET.copy()
    pagination_query.pop("page", None)

    context = {
        "category": category,
        "posts": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "current_sort": sort,
        "pagination_query": pagination_query.urlencode(),
    }
    return render(request, "posts/category_view.html", context)


@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if not (
        request.user == comment.author
        or request.user.has_perm("posts.moderate_comment")
    ):
        messages.error(request, _("You do not have permission to edit this comment."))
        return redirect("post_detail", slug=comment.post.slug)

    if not comment.is_visible:
        raise PermissionDenied

    form = CommentForm(request.POST or None, instance=comment)
    if request.method == "POST" and form.is_valid():
        try:
            update_comment(
                comment=comment,
                content=form.cleaned_data["content"],
                actor=request.user,
            )
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
        except PermissionDenied:
            messages.error(
                request, _("You do not have permission to edit this comment.")
            )
            return redirect("post_detail", slug=comment.post.slug)
        else:
            messages.success(request, _("Comment updated."))
            return redirect("post_detail", slug=comment.post.slug)

    context = {"form": form, "comment": comment}
    return render(request, "posts/comment_edit.html", context)


@login_required
@require_POST
def comment_withdraw(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    try:
        withdraw_comment(comment=comment, actor=request.user)
    except PermissionDenied:
        raise PermissionDenied from None
    messages.success(request, _("Comment withdrawn."))
    return redirect("post_detail", slug=comment.post.slug)


@login_required
@require_POST
def comment_hide(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    try:
        hide_comment(comment=comment, actor=request.user)
    except PermissionDenied:
        raise PermissionDenied from None
    messages.success(request, _("Comment hidden by moderation."))
    return redirect("post_detail", slug=comment.post.slug)


class PostSearchView(ListView):
    model = Post
    template_name = "posts/search_results.html"
    context_object_name = "results"
    paginate_by = 12

    def get_queryset(self):
        queryset = Post.objects.for_listing()

        self.search_form = PostSearchForm(self.request.GET)
        self.search_form.is_valid()
        query = self.search_form.cleaned_data.get("q", "").strip()
        sort_by = self.search_form.cleaned_data.get("sort") or "relevance"

        # Multi-category support (supports both slug and id)
        raw_categories = self.request.GET.getlist("category")
        self.selected_category_slugs = []
        if raw_categories:
            category_filter = Q()
            numeric_ids = []
            string_slugs = []
            for cat_val in raw_categories:
                cat_val = str(cat_val).strip()
                if not cat_val or cat_val.lower() == "all":
                    continue
                if cat_val.isdigit():
                    numeric_ids.append(int(cat_val))
                else:
                    string_slugs.append(cat_val)

            if numeric_ids:
                category_filter |= Q(categories__id__in=numeric_ids)
                id_to_slugs = list(
                    Category.objects.filter(id__in=numeric_ids).values_list(
                        "slug", flat=True
                    )
                )
                self.selected_category_slugs.extend(id_to_slugs)

            if string_slugs:
                category_filter |= Q(categories__slug__in=string_slugs)
                self.selected_category_slugs.extend(string_slugs)

            if category_filter:
                queryset = queryset.filter(category_filter)
        elif self.search_form.cleaned_data.get("category"):
            chosen_cat = self.search_form.cleaned_data["category"]
            queryset = queryset.filter(categories=chosen_cat)
            self.selected_category_slugs.append(chosen_cat.slug)

        if query:
            if connection.vendor == "postgresql":
                vector = (
                    SearchVector("title", weight="A")
                    + SearchVector("excerpt", weight="B")
                    + SearchVector("content", weight="C")
                )
                search_query = SearchQuery(query, search_type="websearch")
                queryset = queryset.annotate(
                    rank=SearchRank(vector, search_query)
                ).filter(rank__gt=0)
            else:
                queryset = queryset.filter(
                    Q(title__icontains=query)
                    | Q(excerpt__icontains=query)
                    | Q(content__icontains=query)
                )

        sort_mapping = {
            "newest": "-created_at",
            "oldest": "created_at",
            "title_asc": "title",
            "title_desc": "-title",
        }
        if sort_by == "relevance" and query and connection.vendor == "postgresql":
            queryset = queryset.order_by("-rank", "-published_at")
        else:
            queryset = queryset.order_by(sort_mapping.get(sort_by, "-published_at"))

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pagination_query = self.request.GET.copy()
        pagination_query.pop("page", None)
        context["form"] = self.search_form
        context["query"] = self.search_form.cleaned_data.get("q", "")
        context["selected_category_slugs"] = getattr(
            self, "selected_category_slugs", []
        )
        context["all_categories"] = Category.objects.all().order_by("name")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_sort"] = self.search_form.cleaned_data.get("sort", "relevance")
        context["pagination_query"] = pagination_query.urlencode()
        return context


class PostCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView
):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    permission_required = "posts.add_post"
    success_message = _("Post created successfully.")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView
):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    permission_required = "posts.change_post"
    success_message = _("Post updated successfully.")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff or self.request.user.has_perm(
            "posts.moderate_comment"
        ):
            return qs
        return qs.filter(author=self.request.user)


class PostDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView
):
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("home")
    permission_required = "posts.delete_post"
    success_message = _("Post deleted successfully.")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff or self.request.user.has_perm(
            "posts.moderate_comment"
        ):
            return qs
        return qs.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)
