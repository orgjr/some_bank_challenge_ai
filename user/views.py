from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from user.serializers import UserSerializer

# Create your views here.


class UserViewSet(ViewSet):
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({"user": f"{user.client.email}"})
