from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import TestCase
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from account.models import Account
from business.models import Business
from person.models import Person
from transaction.models import Transaction
from transaction.serializers import CreateTransferSerializer
from transaction.services.rollback_service import RollbackService
from transaction.services.transfer_processor import TransferProcessor
from user.models import UserModel


def create_person_account(
    email="user@example.com",
    cpf="12345678901",
    name="Usuario Teste",
    number="1000001",
    balance=Decimal("500.00"),
):
    client = UserModel.objects.create_user(
        email=email, password="blabla12", client_type="person"
    )
    Person.objects.create(cpf=cpf, name=name, user=client)
    account = Account.objects.create(client=client, number=number, balance=balance)
    return client, account


def create_business_account(
    email="store@example.com",
    cnpj="12345678000199",
    razao_social="Loja Teste LTDA",
    number="2000001",
    balance=Decimal("500.00"),
):
    client = UserModel.objects.create_user(
        email=email, password="blabla12", client_type="business"
    )
    Business.objects.create(
        cnpj=cnpj,
        razao_social=razao_social,
        nome_fantasia=razao_social,
        user=client,
    )
    account = Account.objects.create(client=client, number=number, balance=balance)
    return client, account


class CreateTransferSerializerTest(TestCase):
    def test_valid_payload_returns_payee_account_and_value(self):
        _, payee = create_person_account()

        serializer = CreateTransferSerializer(
            data={"value": "10.50", "payee": payee.number}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        data = serializer.validated_data
        self.assertEqual(data["payee"], payee)
        self.assertEqual(data["value"], Decimal("10.50"))

    def test_rejects_non_numeric_value(self):
        serializer = CreateTransferSerializer(data={"value": "abc", "payee": 1000001})

        self.assertFalse(serializer.is_valid())
        self.assertIn("value", serializer.errors)

    def test_rejects_invalid_payee_number_format(self):
        serializer = CreateTransferSerializer(data={"value": "10.00", "payee": "abc"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("payee", serializer.errors)

    def test_rejects_missing_required_fields(self):
        serializer = CreateTransferSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("value", serializer.errors)
        self.assertIn("payee", serializer.errors)

    def test_rejects_unknown_payee_account(self):
        serializer = CreateTransferSerializer(data={"value": "10.00", "payee": 9999999})

        self.assertFalse(serializer.is_valid())
        self.assertIn("payee", serializer.errors)
        self.assertIn("payee account not found", str(serializer.errors))


class TransferServiceTest(TestCase):
    @patch(
        "transaction.services.transfer_processor.AuthorizationService.authorization_service_request"
    )
    def test_transfer_moves_balance_and_creates_transaction(self, mock_authorization):
        _, payer = create_person_account(balance=Decimal("100.00"))
        _, payee = create_person_account(
            email="payee@example.com",
            cpf="10987654321",
            name="Favorecido",
            number="1000002",
            balance=Decimal("40.00"),
        )

        TransferProcessor.process(payer=payer, payee=payee, value=Decimal("25.50"))

        payer.refresh_from_db()
        payee.refresh_from_db()
        self.assertEqual(payer.balance, Decimal("74.50"))
        self.assertEqual(payee.balance, Decimal("65.50"))
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertFalse(Transaction.objects.get().refund)
        mock_authorization.assert_called_once()

    @patch(
        "transaction.services.transfer_processor.AuthorizationService.authorization_service_request"
    )
    def test_transfer_rejects_business_as_payer(self, mock_authorization):
        _, payer = create_business_account()
        _, payee = create_person_account(
            email="payee@example.com",
            cpf="10987654321",
            number="1000002",
        )

        with self.assertRaisesMessage(
            ValidationError,
            str({"payer": ["business can not make transfer transactions"]}),
        ):
            TransferProcessor.process(payer=payer, payee=payee, value=Decimal("10.00"))
        mock_authorization.assert_called_once()

    @patch(
        "transaction.services.transfer_processor.AuthorizationService.authorization_service_request"
    )
    def test_transfer_rejects_insufficient_balance(self, mock_authorization):
        _, payer = create_person_account(balance=Decimal("9.99"))
        _, payee = create_person_account(
            email="payee@example.com",
            cpf="10987654321",
            number="1000002",
        )

        with self.assertRaisesMessage(
            ValidationError, str({"payer": ["insuficient founds"]})
        ):
            TransferProcessor.process(payer=payer, payee=payee, value=Decimal("10.00"))
        mock_authorization.assert_called_once()

    @patch(
        "transaction.services.transfer_processor.AuthorizationService.authorization_service_request"
    )
    def test_transfer_rejects_same_account(self, mock_authorization):
        _, payer = create_person_account(balance=Decimal("100.00"))

        with self.assertRaisesMessage(
            ValidationError, str({"transfer": ["cant transfer to same account"]})
        ):
            TransferProcessor.process(payer=payer, payee=payer, value=Decimal("10.00"))
        mock_authorization.assert_called_once()


class RollbackServiceTest(TestCase):
    def test_rollback_reverses_balance_and_marks_refund_transaction(self):
        _, payer = create_person_account(balance=Decimal("75.00"))
        _, payee = create_person_account(
            email="payee@example.com",
            cpf="10987654321",
            number="1000002",
            balance=Decimal("65.00"),
        )

        RollbackService.rollback_due_to_inconsistency(
            payer=payer, payee=payee, value=Decimal("25.00")
        )

        payer.refresh_from_db()
        payee.refresh_from_db()
        transaction = Transaction.objects.get()
        self.assertEqual(payer.balance, Decimal("100.00"))
        self.assertEqual(payee.balance, Decimal("40.00"))
        self.assertTrue(transaction.refund)


class TransactionApiTest(APITestCase):
    def setUp(self):
        self.payer_client, self.payer = create_person_account(balance=Decimal("100.00"))
        _, self.payee = create_person_account(
            email="payee@example.com",
            cpf="10987654321",
            name="Favorecido",
            number="1000002",
            balance=Decimal("40.00"),
        )

    def test_transfer_requires_authentication(self):
        response = self.client.post(
            "/api/v1/transfers/",
            {"value": "10.00", "payee": self.payee.number},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("transaction.services.notification_service.requests.post")
    @patch("transaction.services.authorization_service.requests.get")
    def test_transfer_endpoint_success(self, mock_get, mock_post):
        mock_get.return_value = Mock(
            json=Mock(return_value={"authorized": True}),
            raise_for_status=Mock(return_value=None),
        )
        mock_post.return_value = Mock(raise_for_status=Mock(return_value=None))
        self.client.force_authenticate(user=self.payer_client)

        response = self.client.post(
            "/api/v1/transfers/",
            {"value": "25.00", "payee": self.payee.number},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "value": "25.00",
                "payer": "user@example.com",
                "payee": "payee@example.com",
                "transaction_type": "transfer",
                "operation_date": response.data["operation_date"],
            },
        )
        self.payer.refresh_from_db()
        self.payee.refresh_from_db()
        self.assertEqual(self.payer.balance, Decimal("75.00"))
        self.assertEqual(self.payee.balance, Decimal("65.00"))
        self.assertEqual(Transaction.objects.count(), 1)
        mock_get.assert_called_once()
        mock_post.assert_called_once()

    @patch("transaction.services.transfer_processor.logger.exception")
    @patch("transaction.services.authorization_service.requests.get")
    def test_transfer_endpoint_rejects_when_authorization_fails(
        self, mock_get, mock_logger_exception
    ):
        mock_get.return_value = Mock(
            json=Mock(return_value={"authorized": False}),
            raise_for_status=Mock(side_effect=HTTPError("unauthorized")),
        )
        self.client.force_authenticate(user=self.payer_client)

        response = self.client.post(
            "/api/v1/transfers/",
            {"value": "25.00", "payee": self.payee.number},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.payer.refresh_from_db()
        self.payee.refresh_from_db()
        self.assertEqual(self.payer.balance, Decimal("100.00"))
        self.assertEqual(self.payee.balance, Decimal("40.00"))
        self.assertFalse(Transaction.objects.exists())
        mock_logger_exception.assert_called_once()

    @patch("transaction.services.authorization_service.requests.get")
    def test_transfer_endpoint_rejects_business_rule_errors_after_authorization(
        self, mock_get
    ):
        mock_get.return_value = Mock(raise_for_status=Mock(return_value=None))
        self.client.force_authenticate(user=self.payer_client)

        response = self.client.post(
            "/api/v1/transfers/",
            {"value": "1000.00", "payee": self.payee.number},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_get.assert_called_once()
