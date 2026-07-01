from django.conf import settings
from rest_framework.permissions import AllowAny, BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_superuser
        )


ENV_PERMISSION_CLASS = (
    AllowAny if settings.ENV in {"development", "testing"} else IsSuperUser
)
