from django.core.exceptions import ValidationError
from django.db import models

from user.models import UserModel


# Create your models here.
class Business(models.Model):
    cnpj = models.CharField(max_length=14, unique=True)
    razao_social = models.CharField(max_length=100, unique=True)
    nome_fantasia = models.CharField(max_length=256)
    user = models.OneToOneField(
        UserModel, related_name="business", on_delete=models.CASCADE, default="business"
    )

    def __str__(self):
        return self.razao_social

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.user.client_type != "business":
            raise ValidationError(
                {"client_type": 'business must be client_type="business"'}
            )
