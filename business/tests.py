from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from business.models import Business
from business.serializers import BusinessSerializer
from user.models import UserModel


class BusinessSerializerTest(TestCase):
    def test_create_business_user_model_and_profile(self):
        serializer = BusinessSerializer(
            data={
                "email": "store@example.com",
                "password": "blabla12",
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Loja Teste",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        business = serializer.save()

        self.assertEqual(business.user_model.email, "store@example.com")
        self.assertEqual(business.user_model.client_type, "business")
        self.assertEqual(business.razao_social, "Loja Teste LTDA")
        self.assertTrue(business.user_model.check_password("blabla12"))

    def test_create_requires_valid_email(self):
        serializer = BusinessSerializer(
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

    def test_create_removes_user_model_when_profile_validation_fails(self):
        existing_client = UserModel.objects.create_user(
            email="existing@example.com", password="blabla12", client_type="business"
        )
        Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Existente LTDA",
            nome_fantasia="Loja Existente",
            user_model=existing_client,
        )

        serializer = BusinessSerializer(
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

        self.assertFalse(UserModel.objects.filter(email="new@example.com").exists())


class BusinessTest(TestCase):
    def test_business_must_have_business_client_type(self):
        user_client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )

        store = Business(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            user_model=user_client,
        )

        with self.assertRaisesMessage(
            DjangoValidationError,
            str({"client_type": ['business must be client_type="business"']}),
        ):
            store.save()

    def test_cnpj_and_razao_social_must_be_unique(self):
        first_client = UserModel.objects.create_user(
            email="one@example.com", password="blabla12", client_type="business"
        )
        second_client = UserModel.objects.create_user(
            email="two@example.com", password="blabla12", client_type="business"
        )
        Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Um",
            user_model=first_client,
        )

        with self.assertRaises((DjangoValidationError, IntegrityError)):
            Business.objects.create(
                cnpj="12345678000199",
                razao_social="Loja Teste LTDA",
                nome_fantasia="Loja Dois",
                user_model=second_client,
            )


class StoreApiTest(APITestCase):
    def test_create_business_endpoint(self):
        response = self.client.post(
            "/bank/business/",
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
        self.assertEqual(response.data, {"business": "store@example.com"})
        self.assertTrue(Business.objects.filter(cnpj="12345678000199").exists())

    def test_create_business_endpoint_rejects_missing_required_fields(self):
        response = self.client.post(
            "/bank/business/",
            {"email": "store@example.com", "password": "blabla12"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cnpj", response.data)
        self.assertIn("razao_social", response.data)
        self.assertIn("nome_fantasia", response.data)
