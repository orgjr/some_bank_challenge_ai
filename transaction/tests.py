from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import TestCase
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from account.models import AccountModel
from client.models import ClientModel
from store.models import StoreModel
from transaction.models import TransactionModel
from transaction.serializers import TransactionTransferSerializer
from transaction.services.rollback_service import RollbackService
from transaction.services.transfer_service import TransferService
from user.models import UserModel


def create_user_account(
    email="user@example.com",
    cpf="12345678901",
    name="Usuario Teste",
    number="1000001",
    balance=Decimal("500.00"),
):
    client = ClientModel.objects.create_user(
        email=email, password="blabla12", client_type="user"
    )
    UserModel.objects.create(cpf=cpf, name=name, client=client)
    account = AccountModel.objects.create(client=client, number=number, balance=balance)
    return client, account


def create_store_account(
    email="store@example.com",
    cnpj="12345678000199",
    razao_social="Loja Teste LTDA",
    number="2000001",
    balance=Decimal("500.00"),
):
    client = ClientModel.objects.create_user(
        email=email, password="blabla12", client_type="store"
    )
    StoreModel.objects.create(
        cnpj=cnpj,
        razao_social=razao_social,
        nome_fantasia=razao_social,
        client=client,
    )
    account = AccountModel.objects.create(client=client, number=number, balance=balance)
    return client, account


class TransactionTransferSerializerTest(TestCase):
    def test_valid_payload_returns_payee_account_and_value(self):
        _, payee = create_user_account()

        serializer = TransactionTransferSerializer(
            data={"value": "10.50", "payee": payee.number}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        data = serializer.save()
        self.assertEqual(data["payee"], payee)
        self.assertEqual(data["value"], Decimal("10.50"))

    def test_rejects_non_numeric_value(self):
        serializer = TransactionTransferSerializer(
            data={"value": "abc", "payee": 1000001}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("value", serializer.errors)

    def test_rejects_invalid_payee_number_format(self):
        serializer = TransactionTransferSerializer(
            data={"value": "10.00", "payee": "abc"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("payee", serializer.errors)

    def test_rejects_missing_required_fields(self):
        serializer = TransactionTransferSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("value", serializer.errors)
        self.assertIn("payee", serializer.errors)

    def test_rejects_unknown_payee_account(self):
        serializer = TransactionTransferSerializer(
            data={"value": "10.00", "payee": 9999999}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaisesMessage(
            ValidationError, "Beneficiary account does not exist"
        ):
            serializer.save()


class TransferServiceTest(TestCase):
    def test_transfer_moves_balance_and_creates_transaction(self):
        _, payer = create_user_account(balance=Decimal("100.00"))
        _, payee = create_user_account(
            email="payee@example.com",
            cpf="10987654321",
            name="Favorecido",
            number="1000002",
            balance=Decimal("40.00"),
        )

        TransferService.transfer(
            {"payer": payer, "payee": payee, "value": Decimal("25.50")}
        )

        payer.refresh_from_db()
        payee.refresh_from_db()
        self.assertEqual(payer.balance, Decimal("74.50"))
        self.assertEqual(payee.balance, Decimal("65.50"))
        self.assertEqual(TransactionModel.objects.count(), 1)
        self.assertFalse(TransactionModel.objects.get().refund)

    def test_transfer_rejects_store_as_payer(self):
        _, payer = create_store_account()
        _, payee = create_user_account(
            email="payee@example.com",
            cpf="10987654321",
            number="1000002",
        )

        with self.assertRaisesMessage(
            ValidationError, "Stores can not make transfer transactions"
        ):
            TransferService.transfer(
                {"payer": payer, "payee": payee, "value": Decimal("10.00")}
            )

    def test_transfer_rejects_insufficient_balance(self):
        _, payer = create_user_account(balance=Decimal("9.99"))
        _, payee = create_user_account(
            email="payee@example.com",
            cpf="10987654321",
            number="1000002",
        )

        with self.assertRaisesMessage(ValidationError, "Insuficient founds."):
            TransferService.transfer(
                {"payer": payer, "payee": payee, "value": Decimal("10.00")}
            )

    def test_transfer_requires_payee(self):
        _, payer = create_user_account(balance=Decimal("100.00"))

        with self.assertRaisesMessage(
            ValidationError, "Transfer needs an payee account."
        ):
            TransferService.transfer(
                {"payer": payer, "payee": None, "value": Decimal("10.00")}
            )

    def test_transfer_rejects_same_account(self):
        _, payer = create_user_account(balance=Decimal("100.00"))

        with self.assertRaisesMessage(ValidationError, "Cant transfer to same account"):
            TransferService.transfer(
                {"payer": payer, "payee": payer, "value": Decimal("10.00")}
            )


class RollbackServiceTest(TestCase):
    def test_rollback_reverses_balance_and_marks_refund_transaction(self):
        _, payer = create_user_account(balance=Decimal("75.00"))
        _, payee = create_user_account(
            email="payee@example.com",
            cpf="10987654321",
            number="1000002",
            balance=Decimal("65.00"),
        )

        RollbackService.rollback_due_to_inconsistency(
            {"payer": payer, "payee": payee, "value": Decimal("25.00")}
        )

        payer.refresh_from_db()
        payee.refresh_from_db()
        transaction = TransactionModel.objects.get()
        self.assertEqual(payer.balance, Decimal("100.00"))
        self.assertEqual(payee.balance, Decimal("40.00"))
        self.assertTrue(transaction.refund)


class TransactionApiTest(APITestCase):
    def setUp(self):
        self.payer_client, self.payer = create_user_account(balance=Decimal("100.00"))
        _, self.payee = create_user_account(
            email="payee@example.com",
            cpf="10987654321",
            name="Favorecido",
            number="1000002",
            balance=Decimal("40.00"),
        )

    def test_transfer_requires_authentication(self):
        response = self.client.post(
            "/bank/transaction/transfer/",
            {"value": "10.00", "payee": self.payee.number},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("transaction.views.requests.post")
    @patch("transaction.views.requests.get")
    def test_transfer_endpoint_success(self, mock_get, mock_post):
        mock_get.return_value = Mock(
            json=Mock(return_value={"authorized": True}),
            raise_for_status=Mock(return_value=None),
        )
        mock_post.return_value = Mock(raise_for_status=Mock(return_value=None))
        self.client.force_authenticate(user=self.payer_client)

        response = self.client.post(
            "/bank/transaction/transfer/",
            {"value": "25.00", "payee": self.payee.number},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["transfer"],
            {
                "value": Decimal("25.00"),
                "payer": "Usuario Teste",
                "payee": "Favorecido",
            },
        )
        self.payer.refresh_from_db()
        self.payee.refresh_from_db()
        self.assertEqual(self.payer.balance, Decimal("75.00"))
        self.assertEqual(self.payee.balance, Decimal("65.00"))
        self.assertEqual(TransactionModel.objects.count(), 1)

    @patch("transaction.views.requests.get")
    def test_transfer_endpoint_rolls_back_when_authorization_fails(self, mock_get):
        mock_get.return_value = Mock(
            json=Mock(return_value={"authorized": False}),
            raise_for_status=Mock(side_effect=HTTPError("unauthorized")),
        )
        self.client.force_authenticate(user=self.payer_client)

        response = self.client.post(
            "/bank/transaction/transfer/",
            {"value": "25.00", "payee": self.payee.number},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.payer.refresh_from_db()
        self.payee.refresh_from_db()
        self.assertEqual(self.payer.balance, Decimal("100.00"))
        self.assertEqual(self.payee.balance, Decimal("40.00"))
        self.assertEqual(TransactionModel.objects.filter(refund=False).count(), 1)
        self.assertEqual(TransactionModel.objects.filter(refund=True).count(), 1)

    @patch("transaction.views.requests.get")
    def test_transfer_endpoint_rejects_business_rule_errors_before_authorization(
        self, mock_get
    ):
        self.client.force_authenticate(user=self.payer_client)

        response = self.client.post(
            "/bank/transaction/transfer/",
            {"value": "1000.00", "payee": self.payee.number},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get.assert_not_called()
