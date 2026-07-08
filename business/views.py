from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
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
        responses={
            200: BusinessSerializer(many=True),
            403: OpenApiResponse(description="Access denied in production environment"),
        },
        examples=[
            OpenApiExample(
                "Business list response",
                summary="Example business list response",
                description="Paginated list of all registered business profiles with user email, CNPJ, legal name and trade name.",
                value=[
                    {
                        "user": {"email": "store@example.com"},
                        "cnpj": "12345678000199",
                        "razao_social": "Empresa Exemplo LTDA",
                        "nome_fantasia": "Empresa Exemplo",
                    },
                ],
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        summary="Create a Business user profile",
        description="Creates a new Business profile.",
        tags=["Business"],
        responses={
            201: BusinessSerializer,
            400: OpenApiResponse(description="Validation error - invalid or missing fields"),
        },
        examples=[
            OpenApiExample(
                "Valid business creation",
                summary="Example business creation request",
                description="Request payload containing user credentials, CNPJ, legal name and trade name to create a new business profile.",
                value={
                    "user": {"email": "store@example.com", "password": "seguro123"},
                    "cnpj": "12345678000199",
                    "razao_social": "Empresa Exemplo LTDA",
                    "nome_fantasia": "Empresa Exemplo",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Business created response",
                summary="Example business creation response",
                description="Response confirming the business profile was created, returning the registered data without the password.",
                value={
                    "user": {"email": "store@example.com"},
                    "cnpj": "12345678000199",
                    "razao_social": "Empresa Exemplo LTDA",
                    "nome_fantasia": "Empresa Exemplo",
                },
                response_only=True,
            ),
        ],
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
        responses={
            200: BusinessSerializer,
            400: OpenApiResponse(description="Validation error - invalid or missing fields"),
            404: OpenApiResponse(description="Business profile not found"),
        },
        examples=[
            OpenApiExample(
                "Valid business update",
                summary="Example business update request",
                description="Request payload with all fields to fully replace an existing business profile.",
                value={
                    "user": {"email": "store@example.com", "password": "nova_senha_456"},
                    "cnpj": "12345678000199",
                    "razao_social": "Empresa Exemplo LTDA",
                    "nome_fantasia": "Nome Fantasia Atualizado",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Business updated response",
                summary="Example business update response",
                description="Response containing the updated business profile data after a successful full update.",
                value={
                    "user": {"email": "store@example.com"},
                    "cnpj": "12345678000199",
                    "razao_social": "Empresa Exemplo LTDA",
                    "nome_fantasia": "Nome Fantasia Atualizado",
                },
                response_only=True,
            ),
        ],
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
        responses={
            200: BusinessSerializer,
            400: OpenApiResponse(description="Validation error - invalid fields"),
            404: OpenApiResponse(description="Business profile not found"),
        },
        examples=[
            OpenApiExample(
                "Partial business update",
                summary="Example business partial update request",
                description="Request payload with only the fields to be partially updated (e.g., trade name only).",
                value={
                    "nome_fantasia": "Novo Nome Fantasia",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Business partially updated response",
                summary="Example business partial update response",
                description="Response containing the business profile with only the modified fields updated, other fields remain unchanged.",
                value={
                    "user": {"email": "store@example.com"},
                    "cnpj": "12345678000199",
                    "razao_social": "Empresa Exemplo LTDA",
                    "nome_fantasia": "Novo Nome Fantasia",
                },
                response_only=True,
            ),
        ],
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
        responses={
            204: None,
            404: OpenApiResponse(description="Business profile not found"),
        },
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
