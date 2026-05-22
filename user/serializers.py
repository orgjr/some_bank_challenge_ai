from django.core.exceptions import ValidationError as DjangoValidationError
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

        email = validated_data["email"]
        password = validated_data["password"]
        cpf = validated_data["cpf"]
        name = validated_data["name"]

        client = ClientModel.objects.create_user(
            email=email, password=password, client_type="user"
        )

        try:
            user = UserModel.objects.create(
                cpf=cpf,
                name=name,
                client=client,
            )
            user.save()
        except DjangoValidationError as e:
            client.delete()
            raise ValidationError(e)

        return user
