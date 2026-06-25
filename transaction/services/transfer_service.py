import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import F
from django.db.transaction import atomic
from requests.exceptions import RequestException
from rest_framework.exceptions import ValidationError

from account.models import Account
from transaction.models import Transaction
from transaction.services.authorization_service import AuthorizationService
from transaction.services.rollback_service import RollbackService

logger = logging.getLogger(__name__)


class TransferService:
    ### challenge business rule
    @staticmethod
    def execute_transfer(validated_data):
        transfer_completed = False
        try:
            AuthorizationService.authorization_service_request()
            transaction = Transaction(**validated_data)

            with atomic():
                payer = Account.objects.select_for_update().get(pk=transaction.payer.pk)
                payee = Account.objects.select_for_update().get(pk=transaction.payee.pk)
                transaction.allow_transfer()

                # payer
                payer.balance = F("balance") - transaction.value
                payer.save(update_fields=["balance"])

                # payee
                payee.balance = F("balance") + transaction.value
                payee.save(update_fields=["balance"])

                transaction.save()
                transfer_completed = True

        except DjangoValidationError as e:
            if transfer_completed:
                RollbackService.rollback_due_to_inconsistency(validated_data)
            raise ValidationError(e)
        except RequestException as e:
            logger.exception("authorization service rejected transaction")
            raise ValidationError("unauthorized transaction") from e
