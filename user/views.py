from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, PolymorphicProxySerializer, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from business.models import Business
from business.serializers import BusinessSerializer
from person.models import Person
from person.serializers import PersonSerializer


class GetUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve authenticated user",
        description=(
            "Returns the authenticated user profile based on their account type.\n\n"
            "- Person: returns email, full name and national tax ID\n"
            "- Business: returns email, company tax ID, legal name and trade name"
        ),
        tags=["Users"],
        request=None,
        responses={
            200: PolymorphicProxySerializer(
                component_name="UserProfile",
                serializers=[PersonSerializer, BusinessSerializer],
                resource_type_field_name=None,
            ),
            403: OpenApiResponse(description="Not authenticated"),
            404: OpenApiResponse(description="User profile not found"),
        },
        examples=[
            OpenApiExample(
                "Person user profile response",
                summary="Example person profile response",
                value={
                    "user": {"email": "user@example.com"},
                    "cpf": "12345678901",
                    "name": "João Silva",
                },
                response_only=True,
            ),
            OpenApiExample(
                "Business user profile response",
                summary="Example business profile response",
                value={
                    "user": {"email": "store@example.com"},
                    "cnpj": "12345678000199",
                    "razao_social": "Empresa Exemplo LTDA",
                    "nome_fantasia": "Empresa Exemplo",
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        if request.user.client_type == "person":
            profile = get_object_or_404(Person, user=request.user)
            serializer = PersonSerializer(profile).data
            return Response(serializer, status=status.HTTP_200_OK)

        if request.user.client_type == "business":
            profile = get_object_or_404(Business, user=request.user)
            serializer = BusinessSerializer(profile).data
            return Response(serializer, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)
