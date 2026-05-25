from django.core.exceptions import ValidationError
from django.db import models

from client.models import ClientModel


# Create your models here.
class UserModel(models.Model):
    cpf = models.CharField(max_length=11, unique=True)
    name = models.CharField(max_length=128)
    client = models.OneToOneField(
        ClientModel, related_name="user", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.client.client_type != "user":
            raise ValidationError("Client must be 'user' type.")
