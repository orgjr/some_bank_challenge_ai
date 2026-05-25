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
