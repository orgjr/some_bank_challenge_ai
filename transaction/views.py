import logging

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from transaction.serializers import TransactionTransferSerializer
from transaction.services.notification_service import NotificationService
from transaction.services.transaction_service import TransactionService

# Create your views here.

logger = logging.getLogger(__name__)


class TransactionViewSet(ViewSet):
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def transfer(self, request):
        serializer = TransactionTransferSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        data = {"payer": request.user.account, **serializer.validated_data}

        ### challenge business rule
        TransactionService.execute_transfer(data)
        NotificationService.send_notification(data)
        ###

        return Response(
            {
                "transfer": {
                    "value": data["value"],
                    "payer": request.user.user.name,
                    "payee": data["payee"].client.get_client_name(),
                }
            }
        )
