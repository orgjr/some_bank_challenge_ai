import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from requests.exceptions import RequestException
from rest_framework.exceptions import ValidationError

from transaction.services.authorization_service import AuthorizationService
from transaction.services.notification_service import TransferNotificationService
from transaction.services.rollback_service import RollbackService
from transaction.services.transfer_service import TransferService

logger = logging.getLogger(__name__)


class TransferProcessor:
    @staticmethod
    def process(*, payer, payee, value):
        data = {"payer": payer, "payee": payee, "value": value}
        transfer_completed = False
        try:
            AuthorizationService.authorization_service_request()

            transfer = TransferService.execute_transfer(**data)
            transfer_completed = True

        except DjangoValidationError as e:
            if transfer_completed:
                RollbackService.rollback_due_to_inconsistency(**data)

            raise ValidationError(e)
        except RequestException as e:
            logger.exception("authorization service rejected transaction")
            raise ValidationError("unauthorized transaction") from e

        TransferNotificationService.send(transfer)
        return transfer
