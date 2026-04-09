from sqlalchemy.orm import Session
from model_registry.api.models.user import User
from model_registry.api.models.user_role import UserRole
from model_registry.api.models.role import Role

from sqlalchemy.orm import joinedload

import logging
logger = logging.getLogger(__name__)

def get_user_by_email(db: Session, email: str):
    return (
        db.query(User)
        .options(
            joinedload(User.roles)
            .joinedload(UserRole.role)
            .joinedload(Role.permissions),
            joinedload(User.roles)
            .joinedload(UserRole.laboratory)
        )
        .filter(User.email == email)
        .first()
    )

def create_user(db: Session, email: str, password_hash: str, full_name: str):
    logger.debug(f"Creating user with email: {email} and hashed password: {password_hash}")
    user = User(email=email, full_name=full_name, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user