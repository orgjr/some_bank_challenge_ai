from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account.models import AccountModel


class TransactionTransferSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        error_messages={
            "invalid": "value must be numeric with a maximum of two places after the decimal point"
        },
    )
    payee = serializers.IntegerField(
        error_messages={"invalid": "payee must be a valid account number."}
    )

    def validate_payee(self, value):
        try:
            value = AccountModel.objects.get(number=value)
            return value
        except AccountModel.DoesNotExist:
            raise ValidationError({"detail": "Beneficiary account does not exist"})
