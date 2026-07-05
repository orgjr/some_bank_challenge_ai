from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from business.models import Business
from user.models import UserModel
from user.serializers import UserCredentialsSerializer


class BusinessSerializer(serializers.ModelSerializer):
    user = UserCredentialsSerializer()

    class Meta:
        model = Business
        fields = ["user", "cnpj", "razao_social", "nome_fantasia"]
        extra_kwargs = {
            "cnpj": {
                "help_text": "Brazilian company identifier (CNPJ)",
            },
            "razao_social": {
                "help_text": "Legal company name",
            },
            "nome_fantasia": {
                "help_text": "Trade name / brand name",
            },
        }

    def create(self, validated_data):
        user_model = UserModel()
        try:
            user_model = UserModel.objects.create_user(
                email=validated_data["user"]["email"],
                password=validated_data["user"]["password"],
                client_type="business",
            )

            business = Business.objects.create(
                cnpj=validated_data["cnpj"],
                razao_social=validated_data["razao_social"],
                nome_fantasia=validated_data["nome_fantasia"],
                user=user_model,
            )
            business.save()
        except (DjangoValidationError, IntegrityError, UserModel.DoesNotExist) as e:
            user_model.delete()
            raise ValidationError(e)

        return business

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user = instance.user
            if "email" in user_data:
                user.email = user_data["email"]
            if "password" in user_data:
                user.set_password(user_data["password"])
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
