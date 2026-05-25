from django.core.exceptions import ValidationError
from django.db import models

from client.models import ClientModel


# Create your models here.
class StoreModel(models.Model):
    cnpj = models.CharField(max_length=14, unique=True)
    razao_social = models.CharField(max_length=100, unique=True)
    nome_fantasia = models.CharField(max_length=256)
    client = models.OneToOneField(
        ClientModel, related_name="store", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.razao_social

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.client.client_type != "store":
            raise ValidationError("Client must be 'store' type.")
