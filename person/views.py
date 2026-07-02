from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from person.models import Person
from person.serializers import PersonSerializer
from user.permissions import ENV_PERMISSION_CLASS

# Create your views here.


@extend_schema_view(
    list=extend_schema(
        summary="List all Person Profile registered",
        description=(
            "Lists all Person profiles users registered. \n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to the configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Persons"],
    ),
    create=extend_schema(
        summary="Create a Person user profile",
        description="The client sends a post request to create a Person user profile",
        tags=["Persons"],
    ),
    update=extend_schema(
        summary="Update a Person profile",
        description=(
            "Fully updates the selected Person profile with the provided data.\n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Persons"],
    ),
    partial_update=extend_schema(
        summary="Partially update a Person profile",
        description=(
            "Updates selected fields of the Person profile, keeping all other data unchanged.\n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Persons"],
    ),
    destroy=extend_schema(
        summary="Delete a Person profile",
        description=(
            "A request sent to this endpoint deletes the selected Person user \n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to the configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Persons"],
    ),
)
class PersonViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = PersonSerializer
    queryset = Person.objects.all().order_by("-id")

    def get_permissions(self):
        if self.action in ["list", "update", "destroy"]:
            self.permission_classes = [ENV_PERMISSION_CLASS]
        return super().get_permissions()
