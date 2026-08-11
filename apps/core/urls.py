from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("healthz/", views.health, name="healthz"),
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
