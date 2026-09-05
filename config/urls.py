"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views

from apps.core import views as core_views

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("csp-report/", core_views.csp_report, name="csp_report"),
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("posts/", include("apps.posts.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path(
        "400/",
        default_views.bad_request,
        kwargs={"exception": Exception("Simulated Bad Request")},
        name="simulated_400",
    ),
    path(
        "403/",
        default_views.permission_denied,
        kwargs={"exception": Exception("Simulated Permission Denied")},
        name="simulated_403",
    ),
    path(
        "404/",
        default_views.page_not_found,
        kwargs={"exception": Exception("Simulated Page Not Found")},
        name="simulated_404",
    ),
    path(
        "500/",
        default_views.server_error,
        name="simulated_500",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]
