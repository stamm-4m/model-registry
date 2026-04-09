from model_registry.backend.models.user_model import get_user_by_username
from model_registry.backend.utils.security import check_password
from model_registry.backend.config.settings import settings
import logging
import requests

logger = logging.getLogger(__name__)


def login_request(username: str, password: str):
    """Call backend login endpoint"""
    try:
        response = requests.post(
            f"{settings.API_BASE_URL}/auth/login",
            data={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            logger.debug(f" response: {response.json()}")
            return response.json()

        return None

    except Exception as e:
        logger.error(f"Login error: {e}")
        return None
    

def refresh_token(refresh_token):
    try:
        response = requests.post(
            f"{settings.API_BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        if response.status_code == 200:
            return response.json()

        return None

    except Exception as e:
        print(f"Refresh error: {e}")
        return None