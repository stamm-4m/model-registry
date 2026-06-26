import logging

from sqlalchemy.orm import Session, joinedload

from model_registry.api.models.role import Role
from model_registry.api.models.user import User
from model_registry.api.models.user_role import UserRole

logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str):
    try:
        logger.debug(f"Fetching user by email: {email}")
        return (
            db.query(User)
            .options(
                joinedload(User.roles)
                .joinedload(UserRole.role)
                .joinedload(Role.permissions),
                joinedload(User.roles),
            )
            .filter(User.email == email)
            .first()
        )
    except Exception as e:
        logger.error(
            f"Error occurred while fetching user by email: {email}, Error: {str(e)}"
        )
    return None


def create_user(db: Session, email: str, password_hash: str, full_name: str):
    logger.debug(
        f"Creating user with email: {email} and hashed password: {password_hash}"
    )
    user = User(email=email, full_name=full_name, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
