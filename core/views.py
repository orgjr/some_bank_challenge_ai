from django.contrib.auth import login, logout
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from core.serializers import AuthSerializer


# Create your views here.
class IndexApiView(APIView):
    def get(self, request):
        print(request.user.account.number)
        print(request.user.email)
        return Response({"handshake": "Hello, from my bank_challenge app!"})


class LoginViewSet(ViewSet):
    @action(detail=False, methods=["POST"])
    def login(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request, user)

        return Response({"login": user.email})

    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        user = request.user
        logout(request)
        return Response({"logout": user.email})
