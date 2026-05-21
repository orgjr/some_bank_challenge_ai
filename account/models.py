import uuid

from django.db import models

from user.models import UserModel


# Create your models here.
class AccountModel(models.Model):
    class AccountType(models.TextChoices):
        CONTA_CORRENTE = "CC", "conta corrente"
        POUPANCA = "CP", "conta poupança"

    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, primary_key=True
    )
    client = models.ForeignKey(
        UserModel, related_name="account", on_delete=models.CASCADE
    )
    agency = models.CharField(max_length=4, default=1002)
    number = models.CharField(max_length=7)
    account_type = models.CharField(
        max_length=2, choices=AccountType, default=AccountType.CONTA_CORRENTE
    )
    created_at = models.DateTimeField(auto_now_add=True)
