import logging

from django.db.models import F
from django.db.transaction import atomic

from account.models import Account
from transaction.models import Transaction

logger = logging.getLogger(__name__)


class TransferService:
    ### challenge business rule
    @staticmethod
    def execute_transfer(*, payer, payee, value):
        transaction = Transaction(payer=payer, payee=payee, value=value)

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

            return transaction
