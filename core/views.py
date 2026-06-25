import time
from datetime import datetime

from django.conf import settings
from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from core.serializers import AuthSerializer


# Create your views here.
class IndexApiView(APIView):
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "timestamp": timezone.make_aware(datetime.now()),
                "uptime_seconds": int(time.time() - settings.START_TIME),
            }
        )


class AuthViewSet(ViewSet):
    @action(detail=False, methods=["POST"])
    def login(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request, user)

        return Response({"detail": "ok"})

    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
