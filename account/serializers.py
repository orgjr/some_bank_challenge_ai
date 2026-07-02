from rest_framework import serializers

from account.models import Account


class AccountResponseSerializer(serializers.Serializer):
    client = serializers.CharField(source="client.get_name")
    email = serializers.CharField(source="client.email")
    agency = serializers.CharField()
    number = serializers.CharField()

    class Meta:
        model = Account
