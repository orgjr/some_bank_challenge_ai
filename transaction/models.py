from django.core.exceptions import ValidationError
from django.db import models

from account.models import AccountModel


# Create your models here.
class TransactionModel(models.Model):
    payer = models.ForeignKey(
        AccountModel, related_name="transaction", on_delete=models.PROTECT
    )
    payee = models.ForeignKey(
        AccountModel, on_delete=models.PROTECT, blank=True, null=True
    )

    class TransactionType(models.TextChoices):
        TRANSFER = "TF", "transfer"

    transaction_type = models.CharField(
        max_length=2, choices=TransactionType, default=TransactionType.TRANSFER
    )

    value = models.DecimalField(decimal_places=2, max_digits=8)

    refund = models.BooleanField(default=False)

    operation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.payee:
            return f"{self.payer} * {self.payee} / {self.transaction_type}"
        else:
            return f"{self.payer} / {self.transaction_type}"

    def allow_transfer(self):
        ### challenge business rule
        if self.payer.client.client_type == "store":
            raise ValidationError("Stores can not make transfer transactions")

        if self.value > self.payer.balance:
            raise ValidationError("Insuficient founds.")
        ###

        ### other validations
        if not self.payee:
            raise ValidationError("Transfer needs an payee account.")

        if self.payer == self.payee:
            raise ValidationError("Cant transfer to same account")

        if type(self.payee) is not AccountModel:
            raise ValidationError("Invalid beneficiary account.")
        ###
