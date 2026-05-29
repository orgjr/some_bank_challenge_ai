import requests


class AuthorizationService:
    @staticmethod
    def authorization_service_request():
        ### authorization mock
        response = requests.get(
            "https://util.devi.tools/api/v2/authorize",
            timeout=5,
        )
        response.raise_for_status()
