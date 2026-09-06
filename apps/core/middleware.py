from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.utils import translation


class AppLocaleMiddleware(LocaleMiddleware):
    """Locale middleware that defaults initial visitors to Spanish (settings.LANGUAGE_CODE)

    unless they have explicitly chosen another language via cookie or session.
    """

    def process_request(self, request):
        cookie_language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        session_language = (
            request.session.get(settings.LANGUAGE_COOKIE_NAME)
            or request.session.get("_language")
            if hasattr(request, "session")
            else None
        )

        if cookie_language or session_language:
            super().process_request(request)
            return

        language = settings.LANGUAGE_CODE
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
