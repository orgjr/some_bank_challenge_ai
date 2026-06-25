import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models import Q

from user.manager import UserManager


# Create your models here.
class UserModel(AbstractBaseUser):
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, primary_key=True
    )
    email = models.EmailField(unique=True)

    class ClientType(models.TextChoices):
        BUSINESS = "business", "business"
        PERSON = "person", "person"

    client_type = models.CharField(
        max_length=8, choices=ClientType, null=True, blank=True
    )
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(is_superuser=True) & Q(client_type__isnull=True))
                | (Q(is_superuser=False) & Q(client_type__isnull=False)),
                name="superuser_or_client",
            ),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_client_name(self):
        if hasattr(self, "person"):
            return self.person.name
        if hasattr(self, "business"):
            return self.business.razao_social

        return None
