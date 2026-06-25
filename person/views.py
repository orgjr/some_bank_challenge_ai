from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from person.serializers import PersonSerializer

# Create your views here.


class PersonViewSet(ViewSet):
    def create(self, request):
        serializer = PersonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        person = serializer.save()

        return Response({"person": person.user_model.email})
