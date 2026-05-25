import logging

from requests.exceptions import HTTPError
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

import requests
from transaction.serializers import TransactionTransferSerializer
from transaction.services.rollback_service import RollbackService
from transaction.services.transfer_service import TransferService

# Create your views here.


class TransactionViewSet(ViewSet):
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def transfer(self, request):
        serializer = TransactionTransferSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()

        data = {
            "value": transaction["value"],
            "payer": request.user.account,
            "payee": transaction["payee"],
        }
        TransferService.transfer(data)

        ### challenge business rule
        try:
            response = requests.get("https://util.devi.tools/api/v2/authorize")
            payload = response.json()
            response.raise_for_status()
        except HTTPError as e:
            logging.error({"unauthorized": payload})
            RollbackService.rollback_due_to_inconsistency(data)
            raise PermissionDenied(e)
        ###

        ### challenge business rule
        try:
            response = requests.post("https://util.devi.tools/api/v1/notify", payload)
            response.raise_for_status()
        except HTTPError:
            logging.error("notification error")
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
