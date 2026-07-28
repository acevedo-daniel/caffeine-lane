from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .comment_services import create_comment, hide_comment, withdraw_comment
from .forms import CommentForm, PostForm, PostSearchForm
from .models import Category, Comment, Post


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.published().with_categories(), slug=slug)
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
            messages.error(request, "You must be logged in to comment.")
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
                messages.error(request, "Please correct the errors below.")
            else:
                messages.success(request, "Comment added successfully.")
                return redirect("post_detail", slug=post.slug)

        else:
            messages.error(
                request,
                "There was an error with your comment. Please try again.",
            )
    context = {
        "post": post,
        "comments": comments,
        "form": form,
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
            messages.success(request, "Reply added successfully.")
    else:
        messages.error(request, "Please correct the reply before submitting.")
    return redirect("post_detail", slug=post.slug)


def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.for_listing().filter(categories=category)
    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "posts/category_view.html", context)


@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if not (
        request.user == comment.author
        or request.user.has_perm("posts.moderate_comment")
    ):
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect("post_detail", slug=comment.post.slug)

    if not comment.is_visible:
        raise PermissionDenied

    form = CommentForm(request.POST or None, instance=comment)
    if request.method == "POST" and form.is_valid():
        edited_comment = form.save(commit=False)
        edited_comment.is_edited = True
        edited_comment.save(update_fields=["content", "is_edited", "updated_at"])
        messages.success(request, "Comment edited successfully.")
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
    messages.success(request, "Comment withdrawn.")
    return redirect("post_detail", slug=comment.post.slug)


@login_required
@require_POST
def comment_hide(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    try:
        hide_comment(comment=comment, actor=request.user)
    except PermissionDenied:
        raise PermissionDenied from None
    messages.success(request, "Comment hidden by moderation.")
    return redirect("post_detail", slug=comment.post.slug)


class PostSearchView(ListView):
    model = Post
    template_name = "posts/search_results.html"
    context_object_name = "results"
    paginate_by = 12

    def get_queryset(self):
        queryset = Post.objects.for_listing()

        query = self.request.GET.get("q", "")
        category_id = self.request.GET.get("category", "")
        sort_by = self.request.GET.get("sort", "newest")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).distinct()

        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        sort_mapping = {
            "newest": "-created_at",
            "oldest": "created_at",
            "title_asc": "title",
            "title_desc": "-title",
        }
        order_by_field = sort_mapping.get(sort_by, "-created_at")
        queryset = queryset.order_by(order_by_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostSearchForm(self.request.GET or None)
        context["query"] = self.request.GET.get("q", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_sort"] = self.request.GET.get("sort", "newest")
        return context


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    permission_required = "posts.add_post"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    permission_required = "posts.change_post"


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("home")
    permission_required = "posts.delete_post"
