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

    debit = models.BooleanField()
    credit = models.BooleanField()

    operation_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            if self.payee:
                self.transfer()
            super().save(*args, **kwargs)
        except ValidationError:
            self.rollback_due_to_inconsistency()

    def validate_allowed_transfer(self):
        ### challenge business rule
        if self.payer.client.client_type == "store":
            raise ValidationError("Stores cant realize a transfer transaction")

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

    ### challenge business rule
    def transfer(self):
        self.validate_allowed_transfer()

        self.payer.balance -= self.value
        self.payer.save()
        self.debit = True

        self.payee.balance += self.value
        self.payee.save()
        self.credit = True

        return f"Payer: {self.payer}, Payee: {self.payee}, Value{self.value}"

    def rollback_due_to_inconsistency(self):

        if self.debit is True:
            self.payer.balance += self.value
            self.payer.save()

        if self.credit is True:
            self.payee.balance -= self.value
            self.payee.save()

        return f"Reversed {self.transaction_type} transaction."

    ###
