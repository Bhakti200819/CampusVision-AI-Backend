
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)

from app.auth_database import Base


class UserAssignment(Base):
    __tablename__ = "campusvision_user_assignments"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("campusvision_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assignment_type = Column(String(30), nullable=False)

    assignment_value = Column(String(100), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "assignment_type",
            "assignment_value",
            name="uq_user_assignment",
        ),
    )
