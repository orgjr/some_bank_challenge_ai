import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account.models import Account
from transaction.models import Transaction

logger = logging.getLogger(__name__)


class CreateTransferSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        error_messages={
            "invalid": "value must be numeric with a maximum of two places after the decimal point"
        },
    )
    payee = serializers.IntegerField(
        error_messages={"invalid": "payee must be a valid account number"},
    )

    def validate_payee(self, value):
        try:
            value = Account.objects.get(number=value)
            return value
        except Account.DoesNotExist:
            raise ValidationError({"payee": "payee account not found"})


class ResponseTransferSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=8, decimal_places=2)
    payer = serializers.CharField(source="payer.client")
    payee = serializers.CharField(source="payee.client")
    transaction_type = serializers.CharField(source="get_transaction_type_display")
    operation_date = serializers.DateTimeField()

    class Meta:
        model = Transaction
