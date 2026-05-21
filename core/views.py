from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class IndexApiView(APIView):
    def get(self, request):
        return Response({"handshake": "Hello, from my bank_challenge app!"})
