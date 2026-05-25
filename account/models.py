import random
import uuid

from django.db import models

from client.models import ClientModel


# Create your models here.
class AccountModel(models.Model):
    class AccountType(models.TextChoices):
        CONTA_CORRENTE = "CC", "conta corrente"
        POUPANCA = "CP", "conta poupança"

    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, primary_key=True
    )
    client = models.OneToOneField(
        ClientModel, related_name="account", on_delete=models.CASCADE
    )
    agency = models.CharField(max_length=4, default=1002)
    number = models.CharField(max_length=7)
    account_type = models.CharField(
        max_length=2, choices=AccountType, default=AccountType.CONTA_CORRENTE
    )
    balance = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = random.randrange(pow(10, 6), pow(10, 7))
            self.balance = random.randrange(2000, 10000)

        super().save(*args, **kwargs)
