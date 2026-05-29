import logging

from requests.exceptions import RequestException

import requests

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send_notification(data):
        data = {
            "payer": data["payer"].number,
            "payee": data["payee"].number,
            "value": str(data["value"]),
        }
        try:
            ### notification mock
            response = requests.post(
                "https://util.devi.tools/api/v1/notify",
                json=data,
                timeout=5,
            )
            response.raise_for_status()
        except RequestException:
            logger.exception("Notification service unavailable")
