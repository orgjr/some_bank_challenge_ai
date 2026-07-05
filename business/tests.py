from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from business.models import Business
from business.serializers import BusinessSerializer
from user.models import UserModel


class BusinessSerializerTest(TestCase):
    def test_create_business_user_and_profile(self):
        serializer = BusinessSerializer(
            data={
                "user": {
                    "email": "store@example.com",
                    "password": "blabla12",
                },
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Loja Teste",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        business = serializer.save()

        self.assertEqual(business.user.email, "store@example.com")
        self.assertEqual(business.user.client_type, "business")
        self.assertEqual(business.razao_social, "Loja Teste LTDA")
        self.assertTrue(business.user.check_password("blabla12"))

    def test_create_requires_valid_email(self):
        serializer = BusinessSerializer(
            data={
                "user": {
                    "email": "invalid-email",
                    "password": "blabla12",
                },
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Loja Teste",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)

    def test_create_removes_user_when_profile_validation_fails(self):
        existing_client = UserModel.objects.create_user(
            email="existing@example.com", password="blabla12", client_type="business"
        )
        Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Existente LTDA",
            nome_fantasia="Loja Existente",
            user=existing_client,
        )

        serializer = BusinessSerializer(
            data={
                "user": {
                    "email": "new@example.com",
                    "password": "blabla12",
                },
                "cnpj": "12345678000199",
                "razao_social": "Loja Nova LTDA",
                "nome_fantasia": "Loja Nova",
            }
        )

        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertTrue(
            serializer.errors,
            "{'cnpj': [ErrorDetail(string='business with this cnpj already exists.', code='unique')]}",
        )

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
            user=user_client,
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
            user=first_client,
        )

        with self.assertRaises((DjangoValidationError, IntegrityError)):
            Business.objects.create(
                cnpj="12345678000199",
                razao_social="Loja Teste LTDA",
                nome_fantasia="Loja Dois",
                user=second_client,
            )


class StoreApiTest(APITestCase):
    def test_create_business_endpoint(self):
        response = self.client.post(
            "/api/v1/business/",
            {
                "user": {
                    "email": "store@example.com",
                    "password": "blabla12",
                },
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Loja Teste",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "user": {"email": "store@example.com"},
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Loja Teste",
            },
        )
        self.assertTrue(Business.objects.filter(cnpj="12345678000199").exists())

    def test_create_business_endpoint_rejects_missing_required_fields(self):
        response = self.client.post(
            "/api/v1/business/",
            {"email": "store@example.com", "password": "blabla12"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cnpj", response.data)
        self.assertIn("razao_social", response.data)
        self.assertIn("nome_fantasia", response.data)

    def test_list_business_endpoint(self):
        response = self.client.get("/api/v1/business/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_business_endpoint(self):
        client = UserModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="business"
        )
        business = Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            user=client,
        )
        response = self.client.put(
            f"/api/v1/business/{business.id}/",
            {
                "user": {"email": "store@example.com", "password": "blabla12"},
                "cnpj": "12345678000199",
                "razao_social": "Loja Teste LTDA",
                "nome_fantasia": "Updated Name",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        business.refresh_from_db()
        self.assertEqual(business.nome_fantasia, "Updated Name")

    def test_partial_update_business_endpoint(self):
        client = UserModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="business"
        )
        business = Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            user=client,
        )
        response = self.client.patch(
            f"/api/v1/business/{business.id}/",
            {"nome_fantasia": "Partial Update"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        business.refresh_from_db()
        self.assertEqual(business.nome_fantasia, "Partial Update")

    def test_delete_business_endpoint(self):
        client = UserModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="business"
        )
        business = Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            user=client,
        )
        response = self.client.delete(f"/api/v1/business/{business.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Business.objects.filter(id=business.id).exists())
