from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import Account
from person.models import Person
from user.models import UserModel


class AccountTest(TestCase):
    def test_save_generates_number_and_initial_balance(self):
        client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )

        account = Account.objects.create(client=client)

        self.assertEqual(account.agency, 1002)
        self.assertEqual(len(str(account.number)), 7)
        self.assertGreaterEqual(account.balance, Decimal("2000"))
        self.assertLess(account.balance, Decimal("10000"))

    def test_account_is_one_per_client(self):
        client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )
        Account.objects.create(client=client, number="1000001", balance=100)

        with self.assertRaises(IntegrityError):
            Account.objects.create(client=client, number="1000002", balance=100)


class AccountApiTest(APITestCase):
    def test_create_account_requires_authentication(self):
        response = self.client.post("/bank/account/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_account_for_authenticated_client(self):
        client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )
        Person.objects.create(
            cpf="12345678901", name="Usuario Teste", user_model=client
        )
        self.client.force_authenticate(user=client)

        response = self.client.post("/bank/account/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Usuario Teste", response.data["account"])
        self.assertTrue(Account.objects.filter(client=client).exists())
