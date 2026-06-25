from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from business.models import Business
from user.models import UserModel


class BusinessSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    cnpj = serializers.CharField()
    razao_social = serializers.CharField()
    nome_fantasia = serializers.CharField()

    def create(self, validated_data):
        user_model = UserModel()
        try:
            user_model = UserModel.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                client_type="business",
            )

            business = Business.objects.create(
                cnpj=validated_data["cnpj"],
                razao_social=validated_data["razao_social"],
                nome_fantasia=validated_data["nome_fantasia"],
                user_model=user_model,
            )
            business.save()
        except (DjangoValidationError, IntegrityError, UserModel.DoesNotExist) as e:
            user_model.delete()
            raise ValidationError(e)

        return business
