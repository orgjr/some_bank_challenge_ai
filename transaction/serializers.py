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

    def create(self, validated_data):
        payee = validated_data["payee"]
        try:
            payee_account = AccountModel.objects.get(number=payee)
        except AccountModel.DoesNotExist as e:
            raise ValidationError({"detail": "Beneficiary account does not exist"}, e)

        return {
            "payee": payee_account,
            "value": validated_data["value"],
        }
