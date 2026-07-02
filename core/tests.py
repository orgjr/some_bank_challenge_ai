from rest_framework import status
from rest_framework.test import APITestCase

from user.models import UserModel


class CoreApiTest(APITestCase):
    def test_index_returns_health_check(self):
        response = self.client.get("/api/v1/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "name": "Bank Challenge API",
                "version": "0.9.0",
                "description": "A portfolio project inspired by a coding challenge from a leading digital bank",
                "environment": response.data["environment"],
                "documentation": "/api/v1/docs/",
                "health": "/api/v1/health/",
            },
        )

    def test_login_with_valid_credentials(self):
        UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )

        response = self.client.post(
            "/api/v1/login/",
            {"email": "user@example.com", "password": "blabla12"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "status": "success",
                "message": "Successfully logged in",
            },
        )

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            "/api/v1/login/",
            {"email": "missing@example.com", "password": "wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        response = self.client.post("/api/v1/logout/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_authenticated_user(self):
        client = UserModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="person"
        )
        self.client.force_authenticate(user=client)

        response = self.client.post("/api/v1/logout/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)
