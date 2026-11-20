
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth_database import get_auth_db
from app.auth_dependencies import get_current_user
from app.models.classroom_department import ClassroomDepartment


router = APIRouter(
    prefix="/api",
    tags=["Classroom Departments"]
)


def require_admin(current_user: dict):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )


class ClassroomDepartmentCreate(BaseModel):
    classroom: str
    department: str


@router.get("/classroom-departments")
def get_classroom_departments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    require_admin(current_user)

    records = (
        db.query(ClassroomDepartment)
        .filter(ClassroomDepartment.is_active == True)
        .order_by(ClassroomDepartment.classroom)
        .all()
    )

    return [
        {
            "id": item.id,
            "classroom": item.classroom,
            "department": item.department,
            "is_active": item.is_active
        }
        for item in records
    ]


@router.post("/classroom-departments")
def create_classroom_department(
    data: ClassroomDepartmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    require_admin(current_user)

    classroom = data.classroom.strip()
    department = data.department.strip()

    if not classroom or not department:
        raise HTTPException(
            status_code=400,
            detail="Classroom and department are required"
        )

    record = (
        db.query(ClassroomDepartment)
        .filter(ClassroomDepartment.classroom == classroom)
        .first()
    )

    if record:
        record.department = department
        record.is_active = True
        db.commit()
        db.refresh(record)

        return {
            "message": "Classroom department updated successfully",
            "id": record.id
        }

    record = ClassroomDepartment(
        classroom=classroom,
        department=department,
        is_active=True
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Classroom department created successfully",
        "id": record.id
    }
