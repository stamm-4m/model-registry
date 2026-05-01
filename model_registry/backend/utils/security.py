"""Password hashing utilities for the backend.

Unified with the API service: uses bcrypt via passlib so hashes generated
here are verifiable by ``model_registry.api.core.security.verify_password``.
"""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def check_password(password: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(password, hashed)
    except Exception:
        return False
