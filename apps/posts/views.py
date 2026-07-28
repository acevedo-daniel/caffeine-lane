from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CommentForm, PostForm, PostSearchForm
from .models import Category, Comment, Post


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.published().with_categories(), slug=slug)
    comments = post.comments.filter(is_active=True, parent=None)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect("login")

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()

            messages.success(request, "Comment added successfully!")
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
        request.user == comment.author or request.user.has_perm("posts.change_comment")
    ):
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect("post_detail", slug=comment.post.slug)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        messages.success(request, "Comment edited successfully.")
        return redirect("post_detail", slug=comment.post.slug)

    context = {"form": form, "comment": comment}
    return render(request, "posts/comment_edit.html", context)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if not (
        request.user == comment.author or request.user.has_perm("posts.delete_comment")
    ):
        messages.error(request, "You do not have permission to delete this comment.")
        return redirect("post_detail", slug=comment.post.slug)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect("post_detail", slug=comment.post.slug)

    context = {"comment": comment}
    return render(request, "posts/comment_delete_confirm.html", context)


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
