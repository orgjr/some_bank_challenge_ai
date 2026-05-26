from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from client.models import ClientModel
from store.models import StoreModel
from store.serializers import StoreSerializer


class StoreSerializerTest(TestCase):
    def test_create_store_client_and_profile(self):
        serializer = StoreSerializer(
            data={
                "email": "store@example.com",
                "password": "blabla12",
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Loja Teste",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        store = serializer.save()

        self.assertEqual(store.client.email, "store@example.com")
        self.assertEqual(store.client.client_type, "store")
        self.assertEqual(store.razao_social, "Loja Teste LTDA")
        self.assertTrue(store.client.check_password("blabla12"))

    def test_create_requires_valid_email(self):
        serializer = StoreSerializer(
            data={
                "email": "invalid-email",
                "password": "blabla12",
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Loja Teste",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_create_removes_client_when_profile_validation_fails(self):
        existing_client = ClientModel.objects.create_user(
            email="existing@example.com", password="blabla12", client_type="store"
        )
        StoreModel.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Existente LTDA",
            nome_fantasia="Loja Existente",
            client=existing_client,
        )

        serializer = StoreSerializer(
            data={
                "email": "new@example.com",
                "password": "blabla12",
                "cnpj": "12345678000199",
                "razao_social": "Loja Nova LTDA",
                "nome_fantasia": "Loja Nova",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(ValidationError):
            serializer.save()

        self.assertFalse(ClientModel.objects.filter(email="new@example.com").exists())


class StoreModelTest(TestCase):
    def test_store_must_have_store_type_client(self):
        user_client = ClientModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="user"
        )

        store = StoreModel(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            client=user_client,
        )

        with self.assertRaisesMessage(
            DjangoValidationError, "Client must be 'store' type."
        ):
            store.save()

    def test_cnpj_and_razao_social_must_be_unique(self):
        first_client = ClientModel.objects.create_user(
            email="one@example.com", password="blabla12", client_type="store"
        )
        second_client = ClientModel.objects.create_user(
            email="two@example.com", password="blabla12", client_type="store"
        )
        StoreModel.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Um",
            client=first_client,
        )

        with self.assertRaises((DjangoValidationError, IntegrityError)):
            StoreModel.objects.create(
                cnpj="12345678000199",
                razao_social="Loja Teste LTDA",
                nome_fantasia="Loja Dois",
                client=second_client,
            )


class StoreApiTest(APITestCase):
    def test_create_store_endpoint(self):
        response = self.client.post(
            "/bank/store/",
            {
                "email": "store@example.com",
                "password": "blabla12",
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Loja Teste",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"store": "store@example.com"})
        self.assertTrue(StoreModel.objects.filter(cnpj="12345678000199").exists())

    def test_create_store_endpoint_rejects_missing_required_fields(self):
        response = self.client.post(
            "/bank/store/",
            {"email": "store@example.com", "password": "blabla12"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cnpj", response.data)
        self.assertIn("razao_social", response.data)
        self.assertIn("nome_fantasia", response.data)
