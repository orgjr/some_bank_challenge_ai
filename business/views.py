from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from business.serializers import BusinessSerializer

# Create your views here.


class BusinessViewSet(ViewSet):
    def create(self, request):
        serializer = BusinessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business = serializer.save()

        return Response({"business": business.user_model.email})
