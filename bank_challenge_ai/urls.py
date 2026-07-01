from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from user.permissions import ENV_PERMISSION_CLASS

urlpatterns = [
    path("api/v1/", include("core.urls")),
]

urlpatterns += [
    path(
        "api/v1/openapi/",
        SpectacularAPIView.as_view(permission_classes=[ENV_PERMISSION_CLASS]),
        name="schema",
    ),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema", permission_classes=[ENV_PERMISSION_CLASS]
        ),
        name="swagger-ui",
    ),
    path(
        "api/v1/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema", permission_classes=[ENV_PERMISSION_CLASS]
        ),
        name="redoc",
    ),
]
