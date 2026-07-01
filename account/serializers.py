from rest_framework import serializers

from account.models import Account


class AccountResponseSerializer(serializers.Serializer):
    client = serializers.CharField(source="client.get_name")
    email = serializers.CharField(source="client.email", default="user@example.com")
    agency = serializers.CharField(default="1234")
    number = serializers.CharField(default="1234567")

    class Meta:
        model = Account
