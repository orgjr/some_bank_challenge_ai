from django.db import models

from account.models import AccountModel


# Create your models here.
class TransactionModel(models.Model):
    sender = models.ForeignKey(
        AccountModel, related_name="transaction", on_delete=models.PROTECT
    )
    recipient = models.ForeignKey(AccountModel, on_delete=models.PROTECT)

    class TransactionType(models.TextChoices):
        TRANSFER = "TF", "transfer"

    transaction_type = models.CharField(
        max_length=2, choices=TransactionType, default=TransactionType.TRANSFER
    )

    amount = models.DecimalField(decimal_places=2, max_digits=8)

    operation_date = models.DateTimeField(auto_now_add=True)
