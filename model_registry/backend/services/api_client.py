import requests
import logging
from model_registry.backend.services.auth_service import refresh_token
from model_registry.backend.config.settings import settings

logger = logging.getLogger(__name__)



def authenticated_request(method, endpoint, session_data, **kwargs):
    """
    Make an authenticated HTTP request with automatic token refresh.
    """

    if not session_data or "access_token" not in session_data:
        raise Exception("No authentication session found")

    url = f"{settings.API_BASE_URL}{endpoint}"

    token = session_data.get("access_token")

    headers = kwargs.get("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    kwargs["headers"] = headers

    response = requests.request(method, url, **kwargs)

    # if token expired, try refresh and retry once
    if response.status_code == 401:
        logger.warning("Access token expired, attempting refresh...")

        refresh = session_data.get("refresh_token")

        if not refresh:
            logger.warning("Refresh token failed")
            return None, None

        new_tokens = refresh_token(refresh)

        if not new_tokens:
            logger.warning("Refresh token failed")
            return None, None

        # update session with new tokens
        session_data["access_token"] = new_tokens["access_token"]
        session_data["refresh_token"] = new_tokens["refresh_token"]

        # retry original request with new access token
        headers["Authorization"] = f"Bearer {session_data['access_token']}"
        kwargs["headers"] = headers

        response = requests.request(method, url, **kwargs)

    return response, session_data