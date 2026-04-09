from datetime import datetime, timedelta

from model_registry.api.models.refresh_token import RefreshToken
from sqlalchemy.orm import Session
from model_registry.api.repositories.user_repository import get_user_by_email, create_user
from model_registry.api.core.security import create_refresh_token, hash_password, verify_password, create_access_token
import logging
logger = logging.getLogger(__name__)
# Service functions for user registration and login
def register_user(db: Session, email: str, password: str, full_name: str):
    print(f"Registering user with email: {email} and password: {password}")
    user = get_user_by_email(db, email)
    if user:
        raise Exception("User already exists")
    hashed = hash_password(password)
    return create_user(db, email, hashed, full_name)

def login_user(db: Session, email: str, password: str):
    logger.debug(f"Attempting login for user: {email} with password: {password}")
    user = get_user_by_email(db, email)
    if not user:
        raise Exception("User not found")
    if not verify_password(password, user.password_hash):
        raise Exception("Invalid credentials")
    permissions = [
        rp.permission.name
        for ur in user.roles
        for rp in ur.role.permissions
    ]

    roles = [ur.role.name for ur in user.roles]

    # set access token
    access_token = create_access_token({
        "sub": user.email,
        "permissions": permissions,
        "roles": roles
    })

    # set refresh token
    refresh_token_str = create_refresh_token()

    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    db.add(refresh_token)
    db.commit()

    return access_token, refresh_token_str
