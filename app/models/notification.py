
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)

from app.auth_database import Base


class Notification(Base):
    __tablename__ = "campusvision_notifications"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(String(50), nullable=False, index=True)

    recipient_user_id = Column(
        Integer,
        ForeignKey("campusvision_users.id"),
        nullable=False,
        index=True,
    )

    recipient_role = Column(String(20), nullable=False)

    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    status = Column(String(20), nullable=False, default="UNREAD")

    escalation_level = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    seen_at = Column(DateTime, nullable=True)
    action_taken_at = Column(DateTime, nullable=True)

    email_sent = Column(Boolean, nullable=False, default=False)


class IncidentWorkflow(Base):
    __tablename__ = "campusvision_incident_workflows"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    classroom = Column(String(100), nullable=False)

    current_level = Column(Integer, nullable=False, default=1)

    status = Column(String(20), nullable=False, default="ACTIVE")

    next_escalation_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
