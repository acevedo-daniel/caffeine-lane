from django.conf import settings


def feature_flags(request):
    return {"password_reset_enabled": settings.PASSWORD_RESET_ENABLED}
