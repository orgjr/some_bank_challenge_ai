from django.shortcuts import get_object_or_404
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema
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
        responses=PolymorphicProxySerializer(
            component_name="UserProfile",
            serializers=[PersonSerializer, BusinessSerializer],
            resource_type_field_name=None,
        ),
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
