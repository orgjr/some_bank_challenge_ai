from rest_framework import status
from rest_framework.test import APITestCase

from client.models import ClientModel


class CoreApiTest(APITestCase):
    def test_index_returns_handshake(self):
        response = self.client.get("/bank/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "ok"})

    def test_login_with_valid_credentials(self):
        ClientModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="user"
        )

        response = self.client.post(
            "/bank/auth/login/",
            {"email": "user@example.com", "password": "blabla12"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "ok"})

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            "/bank/auth/login/",
            {"email": "missing@example.com", "password": "wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        response = self.client.post("/bank/auth/logout/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_authenticated_user(self):
        client = ClientModel.objects.create_user(
            email="user@example.com", password="blabla12", client_type="user"
        )
        self.client.force_authenticate(user=client)

        response = self.client.post("/bank/auth/logout/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)
