from rest_framework import serializers

from account.models import AccountModel


class TransactionTransferSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=8, decimal_places=2)
    payee = serializers.IntegerField(
        error_messages={"invalid": "payee must be a valid account number."}
    )

    def create(self, validated_data):
        payee = validated_data["payee"]
        payee_account = AccountModel.objects.get(number=payee)

        return {
            "payee": payee_account,
            "value": validated_data["value"],
        }
