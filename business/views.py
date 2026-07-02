from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from business.models import Business
from business.serializers import BusinessSerializer
from user.permissions import ENV_PERMISSION_CLASS

# Create your views here.


@extend_schema_view(
    list=extend_schema(
        summary="List all Business Profile registered",
        description=(
            "Lists all Business profiles users registered. \n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to the configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Business"],
    ),
    create=extend_schema(
        summary="Create a Business user profile",
        description="Creates a new Business profile.",
        tags=["Business"],
    ),
    update=extend_schema(
        summary="Update a Business profile",
        description=(
            "Fully updates the selected Business profile with the provided data.\n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Business"],
    ),
    partial_update=extend_schema(
        summary="Partially update a Business profile",
        description=(
            "Updates selected fields of the Business profile, keeping all other data unchanged.\n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Business"],
    ),
    destroy=extend_schema(
        summary="Delete a Business profile",
        description=(
            "A request sent to this endpoint deletes the selected Business user \n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to the configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Business"],
    ),
)
class BusinessViewSet(
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = BusinessSerializer
    queryset = Business.objects.all().order_by("-id")

    def get_permissions(self):
        if self.action in ["list", "update", "destroy"]:
            self.permission_classes = [ENV_PERMISSION_CLASS]
        return super().get_permissions()
