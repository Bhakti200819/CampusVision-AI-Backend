
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth_database import get_auth_db
from app.auth_dependencies import get_current_user
from app.models.auth_user import User
from app.models.user_assignment import UserAssignment

router = APIRouter(
    prefix="/api",
    tags=["User Assignments"],
)


def require_admin(current_user: dict):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )


class AssignmentCreate(BaseModel):
    user_id: int
    assignment_type: str
    assignment_value: str


@router.get("/assignments")
def get_assignments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db),
):
    require_admin(current_user)

    records = (
        db.query(UserAssignment)
        .filter(UserAssignment.is_active == True)
        .all()
    )

    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "assignment_type": item.assignment_type,
            "assignment_value": item.assignment_value,
        }
        for item in records
    ]


@router.post("/assignments")
def create_assignment(
    data: AssignmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db),
):
    require_admin(current_user)

    allowed_types = {"classroom", "department", "college"}

    if data.assignment_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid assignment type",
        )

    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    existing = db.query(UserAssignment).filter(
        UserAssignment.user_id == data.user_id,
        UserAssignment.assignment_type == data.assignment_type,
        UserAssignment.assignment_value == data.assignment_value,
    ).first()

    if existing:
        existing.is_active = True
        db.commit()
        return {"message": "Assignment already exists or reactivated"}

    assignment = UserAssignment(
        user_id=data.user_id,
        assignment_type=data.assignment_type,
        assignment_value=data.assignment_value,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": "Assignment created successfully",
        "assignment_id": assignment.id,
    }
