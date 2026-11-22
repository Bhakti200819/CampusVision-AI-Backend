
import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.auth_database import get_auth_db
from app.models.auth_user import User
from app.auth_security import hash_password


router = APIRouter(prefix="/auth", tags=["Admin Setup"])


class AdminSetupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


@router.post("/admin/setup")
def setup_first_admin(
    data: AdminSetupRequest,
    x_admin_setup_key: str = Header(..., alias="X-Admin-Setup-Key"),
    db: Session = Depends(get_auth_db)
):
    setup_key = os.getenv("ADMIN_SETUP_KEY")
    setup_email = os.getenv("ADMIN_SETUP_EMAIL")

    if not setup_key or not setup_email:
        raise HTTPException(
            status_code=503,
            detail="Admin setup is not configured"
        )

    if not secrets.compare_digest(x_admin_setup_key, setup_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid setup key"
        )

    if data.email.lower() != setup_email.strip().lower():
        raise HTTPException(
            status_code=403,
            detail="Email is not authorized for initial Admin setup"
        )

    existing_admin = db.query(User).filter(
        User.role == "admin"
    ).first()

    if existing_admin:
        raise HTTPException(
            status_code=409,
            detail="Admin already exists. Setup is permanently disabled."
        )

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if user:
        user.full_name = data.full_name
        user.hashed_password = hash_password(data.password)
        user.role = "admin"
        user.is_active = True
    else:
        user = User(
            full_name=data.full_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role="admin",
            is_active=True
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    return {
        "message": "Initial Admin account created successfully",
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role
    }

class AdminPasswordResetRequest(BaseModel):
    email: EmailStr
    new_password: str = Field(min_length=12, max_length=128)


@router.post("/admin/reset-password")
def reset_admin_password(
    data: AdminPasswordResetRequest,
    x_admin_setup_key: str = Header(..., alias="X-Admin-Setup-Key"),
    db: Session = Depends(get_auth_db)
):
    setup_key = os.getenv("ADMIN_SETUP_KEY")
    setup_email = os.getenv("ADMIN_SETUP_EMAIL")

    if not setup_key or not setup_email:
        raise HTTPException(status_code=503, detail="Reset is not configured")

    if not secrets.compare_digest(x_admin_setup_key, setup_key):
        raise HTTPException(status_code=403, detail="Invalid setup key")

    if data.email.lower() != setup_email.strip().lower():
        raise HTTPException(status_code=403, detail="Email not authorized")

    user = db.query(User).filter(
        User.email == data.email,
        User.role == "admin"
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Admin account not found")

    user.hashed_password = hash_password(data.new_password)
    user.is_active = True

    db.commit()

    return {"message": "Admin password reset successfully"}
