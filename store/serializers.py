from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from client.models import ClientModel
from store.models import StoreModel


class StoreSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    cnpj = serializers.CharField()
    razao_social = serializers.CharField()
    nome_fantasia = serializers.CharField()

    def create(self, validated_data):
        client = ClientModel()
        try:
            client = ClientModel.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                client_type="store",
            )

            store = StoreModel.objects.create(
                cnpj=validated_data["cnpj"],
                razao_social=validated_data["razao_social"],
                nome_fantasia=validated_data["nome_fantasia"],
                client=client,
            )
            store.save()
        except (DjangoValidationError, ClientModel.DoesNotExist) as e:
            client.delete()
            raise ValidationError(e)

        return store
