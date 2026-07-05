from django.core.exceptions import ValidationError
from django.db import models

from user.models import UserModel


# Create your models here.
class Person(models.Model):
    cpf = models.CharField(max_length=11, unique=True, help_text="Brazilian individual taxpayer identification number (CPF)")
    name = models.CharField(max_length=128, help_text="Full name of the person")
    user = models.OneToOneField(
        UserModel, related_name="person", on_delete=models.CASCADE, default="user"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.user.client_type != "person":
            raise ValidationError(
                {"client_type": 'person must be client_type="person" type'}
            )
