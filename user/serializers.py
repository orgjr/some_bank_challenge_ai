from rest_framework import serializers


class UserCredentialsSerializer(serializers.Serializer):
    email = serializers.EmailField(initial="user@example.com")
    password = serializers.CharField(max_length=128, write_only=True, initial="your_password_123")
