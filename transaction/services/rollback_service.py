from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import F
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError

from account.models import AccountModel
from transaction.models import TransactionModel


class RollbackService:
    ### challenge business rule
    @staticmethod
    @atomic
    def rollback_due_to_inconsistency(validated_data):
        try:
            transaction = TransactionModel(**validated_data)

            payer = AccountModel.objects.select_for_update().get(
                pk=transaction.payer.pk
            )
            payee = AccountModel.objects.select_for_update().get(
                pk=transaction.payee.pk
            )

            # payer
            payer.balance = F("balance") + transaction.value
            payer.save(update_fields=["balance"])

            # payee
            payee.balance = F("balance") - transaction.value
            payee.save(update_fields=["balance"])

            transaction.refund = True
            transaction.save()

        except DjangoValidationError as e:
            raise ValidationError(e)
