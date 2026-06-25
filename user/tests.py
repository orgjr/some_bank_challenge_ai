from django.core.exceptions import ValidationError
from django.test import TestCase

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

    def test_get_client_name_returns_related_person_or_business_name(self):
        person_client = UserModel.objects.create_user(
            email="person@example.com", password="blabla12", client_type="person"
        )
        business_client = UserModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="business"
        )

        from business.models import Business
        from person.models import Person

        Person.objects.create(cpf="12345678901", name="Maria", user_model=person_client)
        Business.objects.create(
            cnpj="12345678000199",
            razao_social="Loja Teste LTDA",
            nome_fantasia="Loja Teste",
            user_model=business_client,
        )

        self.assertEqual(person_client.get_client_name(), "Maria")
        self.assertEqual(business_client.get_client_name(), "Loja Teste LTDA")

    def test_reject_instances_with_create_method(self):

        with self.assertRaisesMessage(NotImplementedError, "Use create_user() instead"):
            UserModel.objects.create(
                email="user@example.com", password="blabla12", client_type="person"
            )

    def test_reject_instances_marked_as_superuser_and_client(self):
        with self.assertRaisesMessage(
            ValidationError,
            str({"__all__": ["Constraint “superuser_or_client” is violated."]}),
        ):
            UserModel.objects.create_user(
                email="user@example.com",
                password="blabla12",
                is_superuser=True,
                client_type="person",
            )
