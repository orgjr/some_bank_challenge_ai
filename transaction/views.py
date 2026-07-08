from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from transaction.models import Transaction
from transaction.serializers import CreateTransferSerializer, ResponseTransferSerializer
from transaction.services.transfer_processor import TransferProcessor
from user.permissions import ENV_PERMISSION_CLASS


# Create your views here.
@extend_schema_view(
    list=extend_schema(
        summary="List all transfers",
        description=(
            "Returns a list of all transfers recorded in the system.\n\n"
            "Access depends on the deployment environment:\n"
            "- Development and testing: available according to configured permissions.\n"
            "- Production: restricted to the superuser."
        ),
        tags=["Transfers"],
        responses={
            200: ResponseTransferSerializer(many=True),
            403: OpenApiResponse(description="Access denied in production environment"),
        },
        examples=[
            OpenApiExample(
                "Transfer list response",
                summary="Example transfer list response",
                description="Paginated list of all transfers with value, payer, payee, transaction type and operation date.",
                value=[
                    {
                        "value": "100.00",
                        "payer": "user@example.com",
                        "payee": "payee@example.com",
                        "transaction_type": "transfer",
                        "operation_date": "2024-01-15T10:30:00Z",
                    },
                ],
                response_only=True,
            ),
        ],
    )
)
class TransferViewSet(GenericViewSet, CreateModelMixin, ListModelMixin):
    queryset = Transaction.objects.all().order_by("-operation_date")

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action == "list":
            self.permission_classes = [ENV_PERMISSION_CLASS]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        self.serializer_class = ResponseTransferSerializer
        if self.action == "create":
            self.serializer_class = CreateTransferSerializer
        return super().get_serializer(*args, **kwargs)

    @extend_schema(
        summary="Create a transfer",
        description=(
            "Creates a transfer by specifying the beneficiary account number "
            "and the transfer amount.\n\n"
            "The request is validated to ensure sufficient funds and compliance "
            "with the system's business rules."
        ),
        tags=["Transfers"],
        responses={
            201: ResponseTransferSerializer,
            400: OpenApiResponse(description="Validation error - invalid data, insufficient funds, or unauthorized transaction"),
            403: OpenApiResponse(description="Not authenticated"),
        },
        examples=[
            OpenApiExample(
                "Valid transfer",
                summary="Example transfer request",
                description="Request payload with the transfer value and the beneficiary account number.",
                value={"value": "100.50", "payee": 1000001},
                request_only=True,
            ),
            OpenApiExample(
                "Transfer created response",
                summary="Example transfer creation response",
                description="Response confirming the transfer was processed, with value, payer email, payee email, transaction type and timestamp.",
                value={
                    "value": "100.50",
                    "payer": "user@example.com",
                    "payee": "payee@example.com",
                    "transaction_type": "transfer",
                    "operation_date": "2024-01-15T10:30:00Z",
                },
                response_only=True,
            ),
        ],
    )
    def create(self, request):
        payer = request.user
        transfer = self.get_serializer(data=request.data)
        transfer.is_valid(raise_exception=True)

        transfer = TransferProcessor.process(
            payer=payer.account,
            payee=transfer.validated_data["payee"],
            value=transfer.validated_data["value"],
        )

        return Response(
            ResponseTransferSerializer(transfer).data, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Retrieve transactions",
        description="Returns all transactions performed by the authenticated user. Currently, only transfer transactions are supported.",
        tags=["Transfers"],
        request=None,
        responses={
            200: ResponseTransferSerializer(many=True),
            403: OpenApiResponse(description="Not authenticated"),
        },
        examples=[
            OpenApiExample(
                "User transfers response",
                summary="Example user transfers response",
                description="List of all transfers performed by the authenticated user, with value, payer, payee, transaction type and date.",
                value=[
                    {
                        "value": "25.00",
                        "payer": "user@example.com",
                        "payee": "payee@example.com",
                        "transaction_type": "transfer",
                        "operation_date": "2024-01-15T10:30:00Z",
                    },
                ],
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["GET"])
    def me(self, request):
        transactions = Transaction.objects.filter(payer=request.user.account).order_by(
            "-operation_date"
        )
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = ResponseTransferSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ResponseTransferSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
