from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from person.models import Person
from person.serializers import PersonSerializer
from user.models import UserModel


class PersonSerializerTest(TestCase):
    def test_create_person_user_and_profile(self):
        serializer = PersonSerializer(
            data={
                "user": {
                    "email": "user@example.com",
                    "password": "blabla12",
                },
                "cpf": "12345678901",
                "name": "Usuario Teste",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.name, "Usuario Teste")
        self.assertEqual(user.user.email, "user@example.com")
        self.assertEqual(user.user.client_type, "person")
        self.assertTrue(user.user.check_password("blabla12"))

    def test_create_requires_valid_email(self):
        serializer = PersonSerializer(
            data={
                "user": {
                    "email": "invalid-email",
                    "password": "blabla12",
                },
                "cpf": "12345678901",
                "name": "Usuario Teste",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)

    def test_create_removes_user_when_profile_validation_fails(self):
        existing_client = UserModel.objects.create_user(
            email="existing@example.com", password="blabla12", client_type="person"
        )
        Person.objects.create(cpf="12345678901", name="Existente", user=existing_client)

        serializer = PersonSerializer(
            data={
                "user": {
                    "email": "new@example.com",
                    "password": "blabla12",
                },
                "cpf": "12345678901",
                "name": "Duplicado",
            }
        )
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.errors, {"cpf": ["person with this cpf already exists."]}
        )
        self.assertFalse(UserModel.objects.filter(email="new@example.com").exists())


class PersonTest(TestCase):
    def test_person_must_have_client_type_person(self):
        store_client = UserModel.objects.create_user(
            email="store@example.com", password="blabla12", client_type="business"
        )

        user = Person(cpf="12345678901", name="Usuario", user=store_client)

        with self.assertRaisesMessage(
            DjangoValidationError,
            str({"client_type": ['person must be client_type="person" type']}),
        ):
            user.save()

    def test_cpf_must_be_unique(self):
        first_client = UserModel.objects.create_user(
            email="one@example.com", password="blabla12", client_type="person"
        )
        second_client = UserModel.objects.create_user(
            email="two@example.com", password="blabla12", client_type="person"
        )
        Person.objects.create(cpf="12345678901", name="Primeiro", user=first_client)

        with self.assertRaises((DjangoValidationError, IntegrityError)):
            Person.objects.create(cpf="12345678901", name="Segundo", user=second_client)


class UserApiTest(APITestCase):
    def test_create_person_endpoint(self):
        response = self.client.post(
            "/api/v1/persons/",
            {
                "user": {
                    "email": "user@example.com",
                    "password": "blabla12",
                },
                "cpf": "12345678901",
                "name": "Usuario Teste",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "user": {
                    "email": "user@example.com",
                },
                "cpf": "12345678901",
                "name": "Usuario Teste",
            },
        )
        self.assertTrue(Person.objects.filter(cpf="12345678901").exists())

    def test_create_person_endpoint_rejects_missing_required_fields(self):
        response = self.client.post(
            "/api/v1/persons/",
            {"email": "user@example.com", "password": "blabla12"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", response.data)
        self.assertIn("name", response.data)

    def test_list_persons_endpoint(self):
        response = self.client.get("/api/v1/persons/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_person_endpoint(self):
        client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )
        person = Person.objects.create(
            cpf="12345678901", name="Usuario Teste", user=client
        )
        response = self.client.put(
            f"/api/v1/persons/{person.id}/",
            {
                "user": {"email": "user@example.com", "password": "blabla12"},
                "cpf": "12345678901",
                "name": "Updated Name",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        person.refresh_from_db()
        self.assertEqual(person.name, "Updated Name")

    def test_partial_update_person_endpoint(self):
        client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )
        person = Person.objects.create(
            cpf="12345678901", name="Usuario Teste", user=client
        )
        response = self.client.patch(
            f"/api/v1/persons/{person.id}/",
            {"name": "Partial Update"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        person.refresh_from_db()
        self.assertEqual(person.name, "Partial Update")

    def test_delete_person_endpoint(self):
        client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )
        person = Person.objects.create(
            cpf="12345678901", name="Usuario Teste", user=client
        )
        response = self.client.delete(f"/api/v1/persons/{person.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Person.objects.filter(id=person.id).exists())
