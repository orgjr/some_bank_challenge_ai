from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from account.models import AccountModel


# Create your views here.
class AccountViewSet(ViewSet):
    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def create(self, request):
        client = request.user
        account = AccountModel.objects.create(client=client)
        client_name = account.client.get_client_name()

        return Response(
            {
                "account": f"client: {client_name}, ag: {account.agency} cc: {account.number}"
            }
        )
