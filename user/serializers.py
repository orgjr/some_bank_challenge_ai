from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from client.models import ClientModel
from user.models import UserModel


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    cpf = serializers.CharField()
    name = serializers.CharField()

    def create(self, validated_data):
        client = ClientModel()

        try:
            client = ClientModel.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                client_type="user",
            )

            user = UserModel.objects.create(
                cpf=validated_data["cpf"],
                name=validated_data["name"],
                client=client,
            )
            user.save()
        except (DjangoValidationError, IntegrityError, ClientModel.DoesNotExist) as e:
            client.delete()
            raise ValidationError(e)

        return user
