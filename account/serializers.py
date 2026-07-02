from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account.models import Account


class AccountResponseSerializer(serializers.Serializer):
    client = serializers.CharField(source="client.get_name")
    email = serializers.CharField(source="client.email")
    agency = serializers.CharField()
    number = serializers.CharField()

    class Meta:
        model = Account


class AccountCreationSerializer(serializers.Serializer):
    def create(self, validated_data):
        user = self.context["user"]
        try:
            return Account.objects.create(client=user)
        except IntegrityError:
            raise ValidationError({"detail": "customer already has an active account"})
