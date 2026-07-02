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
            "cpf": {
                "help_text": "Brazilian individual taxpayer identification number",
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
