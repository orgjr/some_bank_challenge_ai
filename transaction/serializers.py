from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account.models import AccountModel
from transaction.models import TransactionModel


class TransactionTransferSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=8, decimal_places=2)
    payee = serializers.IntegerField(
        error_messages={"invalid": "payee must be a valid account number."}
    )

    def create(self, validated_data):
        request = self.context["request"]
        payer = request.user
        payee = validated_data["payee"]
        payee_account = AccountModel.objects.get(number=payee)

        try:
            transfer = TransactionModel.objects.create(
                payer=payer.account,
                payee=payee_account,
                value=validated_data["value"],
            )
            return transfer
        except DjangoValidationError as e:
            raise ValidationError(e)
