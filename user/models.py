from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class UserModel(AbstractUser):
    cpf = models.CharField(max_length=11)

    def __str__(self):
        return f"{self.email} / {self.get_full_name()}"
