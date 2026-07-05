from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from person.models import Person
from user.models import UserModel
from user.serializers import UserCredentialsSerializer


class PersonSerializer(serializers.ModelSerializer):
    user = UserCredentialsSerializer()

    class Meta:
        model = Person
        fields = ["user", "name", "cpf"]
        extra_kwargs = {
            "name": {
                "help_text": "Full name of the person",
            },
            "cpf": {
                "help_text": "Brazilian individual taxpayer identification number (CPF)",
            },
        }

    def create(self, validated_data):
        user_model = UserModel()

        try:
            user_model = UserModel.objects.create_user(
                email=validated_data["user"]["email"],
                password=validated_data["user"]["password"],
                client_type="person",
            )

            person = Person.objects.create(
                cpf=validated_data["cpf"],
                name=validated_data["name"],
                user=user_model,
            )
            person.save()
        except (DjangoValidationError, IntegrityError, UserModel.DoesNotExist) as e:
            user_model.delete()
            raise ValidationError(e)

        return person

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
