from jose import jwt
import logging
logger = logging.getLogger(__name__)

def get_user_role(session_data):
    logger.debug(f"Getting user role from session data: {session_data}")
    if not session_data or "access_token" not in session_data:
        return None, None
    try:
        payload = jwt.decode(
            session_data["access_token"],
            key=None,  # No key needed since we're not verifying signature
            options={
                "verify_signature": False,
                "verify_exp": False,
            }
        )
        logger.debug("Decoded JWT payload: %s", payload)
        return payload.get("roles"), payload.get("sub")
    except Exception as e:
        logger.error(f"JWT decode error: {e}")
        return None, None