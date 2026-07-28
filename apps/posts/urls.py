from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.PostSearchView.as_view(), name="search"),
    path("new/", views.PostCreateView.as_view(), name="post_create"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
    path("<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("category/<slug:category_slug>/", views.category_view, name="category_view"),
    path("comments/<int:comment_id>/edit/", views.comment_edit, name="comment_edit"),
    path(
        "comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"
    ),
]
