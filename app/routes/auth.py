from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Literal

from app.auth_database import get_auth_db
from app.models.auth_user import User
from app.auth_security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.auth_dependencies import get_current_user
router = APIRouter()



class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Literal["teacher"] = "teacher"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register_user(data: RegisterRequest, db: Session = Depends(get_auth_db)):

    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful",
        "user_id": new_user.id,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "role": new_user.role
    }



@router.post("/login")
def login_user(data: LoginRequest, db: Session = Depends(get_auth_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role
    }
@router.get("/me")
def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "Token verified successfully",
        "user": current_user
    }
class AdminCreateUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Literal["teacher", "hod", "principal", "admin"]


@router.post("/admin/users")
def admin_create_user(
    data: AdminCreateUserRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only Admin can create users"
        )

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "role": new_user.role
    }

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)


@router.get("/admin/users")
def get_admin_users(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only Admin can view users"
        )

    users = db.query(User).all()

    return [
        {
            "user_id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
        for user in users
    ]



@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    user_id = int(current_user.get("sub"))

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different")

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}
