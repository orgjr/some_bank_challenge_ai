from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny

from user.permissions import IsSuperUser

urlpatterns = [
    path("bank/", include("core.urls")),
]

permissions = AllowAny if settings.ENV in {"development", "testing"} else IsSuperUser

urlpatterns += [
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[permissions]),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema", permission_classes=[permissions]
        ),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema", permission_classes=[permissions]
        ),
        name="redoc",
    ),
]
