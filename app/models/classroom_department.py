
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
)

from app.auth_database import Base


class ClassroomDepartment(Base):
    __tablename__ = "campusvision_classroom_departments"

    id = Column(Integer, primary_key=True, index=True)

    classroom = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    department = Column(
        String(100),
        nullable=False,
        index=True,
    )

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
