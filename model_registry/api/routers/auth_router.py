from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from model_registry.api.core.security import create_access_token, get_current_user
from model_registry.api.models.refresh_token import RefreshToken
from model_registry.api.schemas import user
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from model_registry.api.core.database import get_db
from model_registry.api.schemas.user import UserCreate, UserLogin, Token
from model_registry.api.services.auth_service import register_user, login_user
import logging
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = register_user(db, user.email, user.password, user.full_name)
        return {"message": "User created", "email": new_user.email}
    except Exception as e:
        logger.error("Error occurred while registering user: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        access_token, refresh_token = login_user(db, form_data.username, form_data.password)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error("Error occurred while logging in user: %s", str(e))
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/login-json", response_model=Token)
def login_json(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    try:
        access_token, refresh_token = login_user(db, user.email, user.password)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me")
def get_me(user = Depends(get_current_user)):
    return {
        "email": user.email,
        "id": str(user.id)
    }
@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):

    token_db = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    if not token_db or token_db.revoked:
        raise HTTPException(401, "Invalid refresh token")

    if token_db.expires_at < datetime.utcnow():
        raise HTTPException(401, "Refresh token expired")

    user = token_db.user

    # get permissons and roles again in case they were updated
    permissions = [
        rp.permission.name
        for ur in user.roles
        for rp in ur.role.permissions
    ]

    new_access_token = create_access_token({
        "sub": user.email,
        "permissions": permissions,
        "roles": [ur.role.name for ur in user.roles]
    })

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):

    token_db = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    if token_db:
        token_db.revoked = True
        db.commit()

    return {"message": "Logged out"}