from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from model_registry.api.config.settings import settings
from fastapi.security import OAuth2PasswordBearer
from model_registry.api.repositories.user_repository import get_user_by_email
from sqlalchemy.orm import Session
from model_registry.api.core.database import get_db
from fastapi import Depends, HTTPException, status
import secrets
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_refresh_token():
    return secrets.token_urlsafe(64)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        # get data from JWT
        token_permissions = payload.get("permissions", [])
        token_roles = payload.get("roles", [])

    except JWTError:
        raise credentials_exception

    # get user from DB
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    # get permissions and roles from token 
    user.permissions = token_permissions
    user.roles_names = token_roles

    # get role assignments for labs
    user.role_assignments = [
        {
            "role": ur.role.name,
            "lab": ur.laboratory.name,
            "lab_id": ur.laboratory.id
        }
        for ur in user.roles
    ]

    return user