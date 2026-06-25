from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password


class UserManager(BaseUserManager):
    def create(self, *args, **kwargs):
        raise NotImplementedError("Use create_user() instead")

    def create_user(self, email, password=None, client_type=None, **extra_fields):
        if not email:
            raise ValueError("email is required")

        if not password:
            raise ValueError("password is required")

        if extra_fields.get("is_superuser") is not True:
            valid_types = ["business", "person"]
            if client_type not in valid_types:
                raise ValueError({"client_type": 'Must be "business" or "person"'})

        email = self.normalize_email(email)

        user = self.model(email=email, client_type=client_type, **extra_fields)
        validate_password(password)
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, client_type=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusers must have is_superuser=True")

        return self.create_user(email, password, client_type, **extra_fields)
