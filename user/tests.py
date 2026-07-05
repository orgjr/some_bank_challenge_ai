from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from business.models import Business
from person.models import Person
from user.models import UserModel


class UserManagerTest(TestCase):
    def test_create_user_requires_email(self):
        with self.assertRaisesMessage(ValueError, "email is required"):
            UserModel.objects.create_user(
                email="", password="blabla12", client_type="person"
            )

    def test_create_user_requires_password(self):
        with self.assertRaisesMessage(ValueError, "password is required"):
            UserModel.objects.create_user(
                email="user@example.com", password="", client_type="person"
            )

    def test_create_user_requires_valid_client_type(self):
        with self.assertRaisesMessage(
            ValueError, str({"client_type": 'Must be "business" or "person"'})
        ):
            UserModel.objects.create_user(
                email="user@example.com", password="blabla12", client_type="admin"
            )

    def test_validate_password_size(self):
        with self.assertRaisesMessage(
            ValidationError,
            "This password is too short. It must contain at least 8 characters",
        ):
            UserModel.objects.create_user(
                email="user@example.com", password="a123", client_type="person"
            )

    def test_validate_password_strength_numeric(self):
        with self.assertRaisesMessage(
            ValidationError,
            "['This password is too common.', 'This password is entirely numeric.']",
        ):
            UserModel.objects.create_user(
                email="user@example.com", password="12345678", client_type="person"
            )

    def test_validate_password_strength(self):
        with self.assertRaisesMessage(
            ValidationError,
            "This password is too common.",
        ):
            UserModel.objects.create_user(
                email="user@example.com", password="senha123", client_type="person"
            )

    def test_create_user_normalizes_email_and_hashes_password(self):
        client = UserModel.objects.create_user(
            email="USER@EXAMPLE.COM",
            password="blabla12",
            client_type="person",
        )

        self.assertEqual(client.email, "USER@example.com")
        self.assertTrue(client.check_password("blabla12"))
        self.assertNotEqual(client.password, "blabla12")

    def test_get_name_returns_related_person_or_business_name(self):
        person_client = UserModel.objects.create_user(
            email="person@example.com", password="blabla12", client_type="person"
        )
        business_client = UserModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="business"
        )

        from business.models import Business
        from person.models import Person

        Person.objects.create(cpf="12345678901", name="Maria", user=person_client)
        Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            user=business_client,
        )

        self.assertEqual(person_client.get_name(), "Maria")
        self.assertEqual(business_client.get_name(), "Loja Teste LTDA")

    def test_reject_instances_with_create_method(self):

        with self.assertRaisesMessage(NotImplementedError, "Use create_user() instead"):
            UserModel.objects.create(
                email="user@example.com", password="blabla12", client_type="person"
            )

    def test_reject_instances_marked_as_superuser_and_client(self):
        with self.assertRaisesMessage(
            ValidationError,
            str({"__all__": ["Constraint \u201csuperuser_or_client\u201d is violated."]}),
        ):
            UserModel.objects.create_user(
                email="user@example.com",
                password="blabla12",
                is_superuser=True,
                client_type="person",
            )


class UserApiTest(APITestCase):
    def test_get_user_me_requires_authentication(self):
        response = self.client.get("/api/v1/users/me/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_me_person(self):
        client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )
        Person.objects.create(cpf="12345678901", name="Usuario Teste", user=client)
        self.client.force_authenticate(user=client)

        response = self.client.get("/api/v1/users/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "user@example.com")
        self.assertEqual(response.data["cpf"], "12345678901")
        self.assertEqual(response.data["name"], "Usuario Teste")

    def test_get_user_me_business(self):
        client = UserModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="business"
        )
        Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            user=client,
        )
        self.client.force_authenticate(user=client)

        response = self.client.get("/api/v1/users/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "store@example.com")
        self.assertEqual(response.data["cnpj"], "12345678000199")
        self.assertEqual(response.data["razao_social"], "Loja Teste LTDA")
