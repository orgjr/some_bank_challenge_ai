from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from client.models import ClientModel
from user.models import UserModel
from user.serializers import UserSerializer


class UserSerializerTest(TestCase):
    def test_create_user_client_and_profile(self):
        serializer = UserSerializer(
            data={
                "email": "user@example.com",
                "password": "blabla12",
                "cpf": "12345678901",
                "name": "Usuario Teste",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.name, "Usuario Teste")
        self.assertEqual(user.client.email, "user@example.com")
        self.assertEqual(user.client.client_type, "user")
        self.assertTrue(user.client.check_password("blabla12"))

    def test_create_requires_valid_email(self):
        serializer = UserSerializer(
            data={
                "email": "invalid-email",
                "password": "blabla12",
                "cpf": "12345678901",
                "name": "Usuario Teste",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_create_removes_client_when_profile_validation_fails(self):
        existing_client = ClientModel.objects.create_user(
            email="existing@example.com", password="blabla12", client_type="user"
        )
        UserModel.objects.create(
            cpf="12345678901", name="Existente", client=existing_client
        )

        serializer = UserSerializer(
            data={
                "email": "new@example.com",
                "password": "blabla12",
                "cpf": "12345678901",
                "name": "Duplicado",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(ValidationError):
            serializer.save()

        self.assertFalse(ClientModel.objects.filter(email="new@example.com").exists())


class UserModelTest(TestCase):
    def test_user_must_have_user_type_client(self):
        store_client = ClientModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="store"
        )

        user = UserModel(cpf="12345678901", name="Usuario", client=store_client)

        with self.assertRaisesMessage(
            DjangoValidationError, "Client must be 'user' type."
        ):
            user.save()

    def test_cpf_must_be_unique(self):
        first_client = ClientModel.objects.create_user(
            email="one@example.com", password="blabla12", client_type="user"
        )
        second_client = ClientModel.objects.create_user(
            email="two@example.com", password="blabla12", client_type="user"
        )
        UserModel.objects.create(
            cpf="12345678901", name="Primeiro", client=first_client
        )

        with self.assertRaises((DjangoValidationError, IntegrityError)):
            UserModel.objects.create(
                cpf="12345678901", name="Segundo", client=second_client
            )


class UserApiTest(APITestCase):
    def test_create_user_endpoint(self):
        response = self.client.post(
            "/bank/user/",
            {
                "email": "user@example.com",
                "password": "blabla12",
                "cpf": "12345678901",
                "name": "Usuario Teste",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"user": "user@example.com"})
        self.assertTrue(UserModel.objects.filter(cpf="12345678901").exists())

    def test_create_user_endpoint_rejects_missing_required_fields(self):
        response = self.client.post(
            "/bank/user/",
            {"email": "user@example.com", "password": "blabla12"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", response.data)
        self.assertIn("name", response.data)
