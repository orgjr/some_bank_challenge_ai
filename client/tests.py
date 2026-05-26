from django.core.exceptions import ValidationError
from django.test import TestCase

from client.models import ClientModel


class ClientManagerTest(TestCase):
    def test_create_user_requires_email(self):
        with self.assertRaisesMessage(ValueError, "email is required"):
            ClientModel.objects.create_user(
                email="", password="blabla12", client_type="user"
            )

    def test_create_user_requires_password(self):
        with self.assertRaisesMessage(ValueError, "password is required"):
            ClientModel.objects.create_user(
                email="user@example.com", password="", client_type="user"
            )

    def test_create_user_requires_valid_client_type(self):
        with self.assertRaisesMessage(
            ValueError, "Client type must be 'store' or 'user'"
        ):
            ClientModel.objects.create_user(
                email="user@example.com", password="blabla12", client_type="admin"
            )

    def test_validate_password_size(self):
        with self.assertRaisesMessage(
            ValidationError,
            "This password is too short. It must contain at least 8 characters",
        ):
            ClientModel.objects.create_user(
                email="user@example.com", password="a123", client_type="user"
            )

    def test_validate_password_strength_numeric(self):
        with self.assertRaisesMessage(
            ValidationError,
            "['This password is too common.', 'This password is entirely numeric.']",
        ):
            ClientModel.objects.create_user(
                email="user@example.com", password="12345678", client_type="user"
            )

    def test_validate_password_strength(self):
        with self.assertRaisesMessage(
            ValidationError,
            "This password is too common.",
        ):
            ClientModel.objects.create_user(
                email="user@example.com", password="senha123", client_type="user"
            )

    def test_create_user_normalizes_email_and_hashes_password(self):
        client = ClientModel.objects.create_user(
            email="USER@EXAMPLE.COM",
            password="blabla12",
            client_type="user",
        )

        self.assertEqual(client.email, "USER@example.com")
        self.assertTrue(client.check_password("blabla12"))
        self.assertNotEqual(client.password, "blabla12")

    def test_get_client_name_returns_related_user_or_store_name(self):
        user_client = ClientModel.objects.create_user(
            email="person@example.com", password="blabla12", client_type="user"
        )
        store_client = ClientModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="store"
        )

        from store.models import StoreModel
        from user.models import UserModel

        UserModel.objects.create(cpf="12345678901", name="Maria", client=user_client)
        StoreModel.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            client=store_client,
        )

        self.assertEqual(user_client.get_client_name(), "Maria")
        self.assertEqual(store_client.get_client_name(), "Loja Teste LTDA")
