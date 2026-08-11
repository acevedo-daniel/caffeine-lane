from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.PostSearchView.as_view(), name="search"),
    path("new/", views.PostCreateView.as_view(), name="post_create"),
    path("category/<slug:category_slug>/", views.category_view, name="category_view"),
    path("<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("comments/<int:comment_id>/edit/", views.comment_edit, name="comment_edit"),
    path("comments/<int:comment_id>/reply/", views.comment_reply, name="comment_reply"),
    path(
        "comments/<int:comment_id>/withdraw/",
        views.comment_withdraw,
        name="comment_withdraw",
    ),
    path("comments/<int:comment_id>/hide/", views.comment_hide, name="comment_hide"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
]
