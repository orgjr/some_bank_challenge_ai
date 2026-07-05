from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
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
        responses={
            200: PersonSerializer(many=True),
            403: OpenApiResponse(description="Access denied in production environment"),
        },
        examples=[
            OpenApiExample(
                "Person list response",
                summary="Example person list response",
                value=[
                    {
                        "user": {"email": "joao@example.com"},
                        "cpf": "12345678901",
                        "name": "João Silva",
                    },
                ],
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        summary="Create a Person user profile",
        description="The client sends a post request to create a Person user profile",
        tags=["Persons"],
        responses={
            201: PersonSerializer,
            400: OpenApiResponse(description="Validation error - invalid or missing fields"),
        },
        examples=[
            OpenApiExample(
                "Valid person creation",
                summary="Example person creation request",
                value={
                    "user": {"email": "joao@example.com", "password": "seguro123"},
                    "cpf": "12345678901",
                    "name": "João Silva",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Person created response",
                summary="Example person creation response",
                value={
                    "user": {"email": "joao@example.com"},
                    "cpf": "12345678901",
                    "name": "João Silva",
                },
                response_only=True,
            ),
        ],
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
        responses={
            200: PersonSerializer,
            400: OpenApiResponse(description="Validation error - invalid or missing fields"),
            404: OpenApiResponse(description="Person profile not found"),
        },
        examples=[
            OpenApiExample(
                "Valid person update",
                summary="Example person update request",
                value={
                    "user": {"email": "joao@example.com", "password": "nova_senha_456"},
                    "cpf": "12345678901",
                    "name": "João Silva Atualizado",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Person updated response",
                summary="Example person update response",
                value={
                    "user": {"email": "joao@example.com"},
                    "cpf": "12345678901",
                    "name": "João Silva Atualizado",
                },
                response_only=True,
            ),
        ],
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
        responses={
            200: PersonSerializer,
            400: OpenApiResponse(description="Validation error - invalid fields"),
            404: OpenApiResponse(description="Person profile not found"),
        },
        examples=[
            OpenApiExample(
                "Partial person update",
                summary="Example person partial update request",
                value={
                    "name": "Nome Parcialmente Atualizado",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Person partially updated response",
                summary="Example person partial update response",
                value={
                    "user": {"email": "joao@example.com"},
                    "cpf": "12345678901",
                    "name": "Nome Parcialmente Atualizado",
                },
                response_only=True,
            ),
        ],
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
        responses={
            204: None,
            404: OpenApiResponse(description="Person profile not found"),
        },
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
