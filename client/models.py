import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from client.manager import ClientManager


# Create your models here.
class ClientModel(AbstractBaseUser):
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, primary_key=True
    )
    email = models.EmailField(unique=True)

    class ClientType(models.TextChoices):
        STORE = "store", "store"
        USER = "user", "user"

    client_type = models.CharField(max_length=5, choices=ClientType)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["client_type"]

    objects = ClientManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_client_name(self):
        if hasattr(self, "user"):
            return self.user.name
        if hasattr(self, "store"):
            return self.store.razao_social

        return None
