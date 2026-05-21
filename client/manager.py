from django.contrib.auth.base_user import BaseUserManager


class ClientManager(BaseUserManager):
    def create_user(self, email, password=None, client_type=None, **extra_fields):
        if not email:
            raise ValueError("email is required")

        if not password:
            raise ValueError("password is required")

        valid_types = ["store", "user"]
        if client_type not in valid_types:
            raise ValueError("Client type must be 'store' or 'user'")

        email = self.normalize_email(email)

        user = self.model(email=email, client_type=client_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, client_type=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be a staff (is_staff == True).")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be a superuser (is_superuser == True).")

        return self.create_user(email, password, client_type, **extra_fields)
