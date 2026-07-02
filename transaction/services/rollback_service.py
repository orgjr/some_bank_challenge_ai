import logging

from django.db.models import F
from django.db.transaction import atomic

from account.models import Account
from transaction.models import Transaction

logger = logging.getLogger(__name__)


class RollbackService:
    ### challenge business rule
    @staticmethod
    @atomic
    def rollback_due_to_inconsistency(*, payer, payee, value):
        try:
            rollback = Transaction(payer=payer, payee=payee, value=value)

            payer = Account.objects.select_for_update().get(pk=rollback.payer.pk)
            payee = Account.objects.select_for_update().get(pk=rollback.payee.pk)

            # payer
            payer.balance = F("balance") + rollback.value
            payer.save(update_fields=["balance"])

            # payee
            payee.balance = F("balance") - rollback.value
            payee.save(update_fields=["balance"])

            rollback.refund = True
            rollback.save()

            return rollback
        except Exception:
            logger.exception({"Rollback failed"})
            raise
