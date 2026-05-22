from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from store.serializers import StoreSerializer

# Create your views here.


class StoreViewSet(ViewSet):
    def create(self, request):
        serializer = StoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store = serializer.save()

        return Response({"store": store.client.email})
