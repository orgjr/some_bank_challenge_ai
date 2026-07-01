from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from user.permissions import ENV_PERMISSION_CLASS

urlpatterns = [
    path("bank/", include("core.urls")),
]

urlpatterns += [
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[ENV_PERMISSION_CLASS]),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema", permission_classes=[ENV_PERMISSION_CLASS]
        ),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema", permission_classes=[ENV_PERMISSION_CLASS]
        ),
        name="redoc",
    ),
]
