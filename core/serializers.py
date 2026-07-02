from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class IndexResponseSerializer(serializers.Serializer):
    name = serializers.CharField()
    version = serializers.CharField()
    description = serializers.CharField()
    environment = serializers.CharField()
    documentation = serializers.CharField()
    health = serializers.CharField()


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    uptime_seconds = serializers.IntegerField()


class LoginResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)

        if user is None:
            raise ValidationError("invalid credentials.")

        data["user"] = user
        return data
