from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import F
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError

from account.models import AccountModel
from transaction.models import TransactionModel


class TransferService:
    ### challenge business rule
    @staticmethod
    @atomic
    def transfer(validated_data):
        try:
            transaction = TransactionModel(**validated_data)
            transaction.allowed_transfer()

            payer = AccountModel.objects.select_for_update().get(
                pk=transaction.payer.pk
            )
            payee = AccountModel.objects.select_for_update().get(
                pk=transaction.payee.pk
            )

            # payer
            payer.balance = F("balance") - transaction.value
            payer.save(update_fields=["balance"])

            # payee
            payee.balance = F("balance") + transaction.value
            payee.save(update_fields=["balance"])

            transaction.save()

            return f"Payer: {transaction.payer}, Payee: {transaction.payee}, Value: {transaction.value}"
        except DjangoValidationError as e:
            raise ValidationError(e)
