import time
from datetime import datetime

from django.conf import settings
from django.contrib.auth import login, logout
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from core.serializers import (
    AuthSerializer,
    HealthResponseSerializer,
    IndexResponseSerializer,
    LoginResponseSerializer,
)


# Create your views here.
class IndexAPIView(APIView):
    @extend_schema(
        summary="API index",
        description="Returns general information about the API, including its version and the available documentation and health check endpoints",
        tags=["Index"],
        request=None,
        responses={200: IndexResponseSerializer},
        examples=[
            OpenApiExample(
                "Index response",
                summary="Example index response",
                value={
                    "name": "Bank Challenge API",
                    "version": "0.9.0",
                    "description": "A portfolio project inspired by a coding challenge from a leading digital bank",
                    "environment": "development",
                    "documentation": "/api/v1/docs/",
                    "health": "/api/v1/health/",
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        data = {
            "name": "Bank Challenge API",
            "version": "0.9.0",
            "description": "A portfolio project inspired by a coding challenge from a leading digital bank",
            "environment": settings.ENV,
            "documentation": "/api/v1/docs/",
            "health": "/api/v1/health/",
        }
        return Response(data, status=status.HTTP_200_OK)


class HealthCheckAPIView(APIView):
    @extend_schema(
        summary="Check system status",
        description="Returns the current system status, including the server timestamp and application uptime. This endpoint can be used as a health check",
        tags=["Health"],
        request=None,
        responses={200: HealthResponseSerializer},
        examples=[
            OpenApiExample(
                "Health response",
                summary="Example health check response",
                value={
                    "status": "ok",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "uptime_seconds": 3600,
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "timestamp": timezone.make_aware(datetime.now()),
                "uptime_seconds": int(time.time() - settings.START_TIME),
            },
            status=status.HTTP_200_OK,
        )


class AuthViewSet(ViewSet):
    @extend_schema(
        summary="Authenticate user",
        description="Authenticates a registered user using their email address and password and starts a new session",
        tags=["Login"],
        request=AuthSerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiResponse(description="Invalid email or password"),
        },
        examples=[
            OpenApiExample(
                "Valid login",
                summary="Example login request",
                value={"email": "user@example.com", "password": "your_password_123"},
                request_only=True,
            ),
            OpenApiExample(
                "Login success response",
                summary="Example login success response",
                value={
                    "status": "success",
                    "message": "Successfully logged in",
                },
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["POST"])
    def login(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request, user)

        return Response(
            {
                "status": "success",
                "message": "Successfully logged in",
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Log out",
        description="Ends the current authenticated user's session",
        tags=["Logout"],
        request=None,
        responses={
            204: None,
            403: OpenApiResponse(description="Not authenticated"),
        },
    )
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
