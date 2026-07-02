import logging

from django.core.exceptions import ValidationError
from requests.exceptions import RequestException

import requests
from transaction.models import Transaction

logger = logging.getLogger(__name__)


class TransferNotificationService:
    @staticmethod
    def send(transaction: Transaction):
        if not isinstance(transaction, Transaction):
            raise ValidationError("this is not a valid transaction")
        payload = {
            "transaction_id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "payer_email": transaction.payer.client.email,
            "payer_name": transaction.payer.client.get_name(),
            "payee_email": transaction.payee.client.email,
            "payee_name": transaction.payee.client.get_name(),
            "value": str(transaction.value),
            "transaction_date": str(transaction.operation_date),
        }

        try:
            ### notification mock
            response = requests.post(
                "https://util.devi.tools/api/v1/notify",
                json=payload,
                timeout=5,
            )
            response.raise_for_status()
        except RequestException:
            logger.exception("Notification service unavailable")
