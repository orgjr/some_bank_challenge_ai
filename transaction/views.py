import logging

from requests.exceptions import HTTPError
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

import requests
from transaction.serializers import TransactionTransferSerializer

# Create your views here.


class TransactionViewSet(ViewSet):
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def transfer(self, request):

        ### challenge business rule
        try:
            response = requests.get("https://util.devi.tools/api/v2/authorize")
            payload = response.json()
            response.raise_for_status()
        except HTTPError as e:
            logging.error({"unauthorized": payload})
            raise PermissionDenied(e)
        ###

        serializer = TransactionTransferSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        transfer = serializer.save()
        payer_name = transfer.payer.client.get_client_name()
        payee_name = transfer.payee.client.get_client_name()

        ### challenge business rule
        try:
            response = requests.post(
                "https://util.devi.tools/api/v1/notify",
                data={
                    "value": {transfer.value},
                    "payer": {payer_name},
                    "payee": {payee_name},
                },
            )
            response.raise_for_status()
        except HTTPError:
            logging.error("notification error")
            ###

        return Response(
            {
                "transfer": {
                    "value": {transfer.value},
                    "payer": {payer_name},
                    "payee": {payee_name},
                },
            }
        )
