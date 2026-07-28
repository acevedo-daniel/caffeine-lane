# Register your models here.
from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "birth_date", "gender", "created_at")
    search_fields = ("user__username", "user__email")
