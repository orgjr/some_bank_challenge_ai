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

    def clean(self):
        required_fields = [
            self.email,
            self.password,
            self.cnpj,
            self.razao_social,
            self.nome_fantasia,
        ]
        for required in required_fields:
            if not required:
                raise ValidationError(
                    "Store accounts must have email, password, cnpj, razao_social and nome_fantasia."
                )

        if self.client.client_type is not ClientModel.ClientType.STORE:
            raise ValidationError("Client must be STORE type.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
