
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth_database import get_auth_db
from app.auth_dependencies import get_current_user
from app.models.notification import Notification


router = APIRouter(
    prefix="/api",
    tags=["Notifications"]
)


def get_user_id(current_user: dict):
    try:
        return int(current_user.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid user authentication"
        )


@router.get("/notifications")
def get_my_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    user_id = get_user_id(current_user)

    notifications = (
        db.query(Notification)
        .filter(Notification.recipient_user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "incident_id": item.incident_id,
            "recipient_role": item.recipient_role,
            "title": item.title,
            "message": item.message,
            "status": item.status,
            "escalation_level": item.escalation_level,
            "created_at": item.created_at.isoformat(),
            "seen_at": (
                item.seen_at.isoformat()
                if item.seen_at else None
            ),
            "action_taken_at": (
                item.action_taken_at.isoformat()
                if item.action_taken_at else None
            ),
            "email_sent": item.email_sent
        }
        for item in notifications
    ]


@router.patch("/notifications/{notification_id}/seen")
def mark_notification_seen(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    user_id = get_user_id(current_user)

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.recipient_user_id == user_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if notification.action_taken_at is None:
        notification.status = "SEEN"

    if notification.seen_at is None:
        notification.seen_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Notification marked as seen",
        "status": notification.status
    }


@router.patch("/notifications/{notification_id}/action-taken")
def mark_action_taken(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_auth_db)
):
    user_id = get_user_id(current_user)

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.recipient_user_id == user_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if notification.action_taken_at is None:
        now = datetime.utcnow()
        notification.action_taken_at = now
        notification.status = "ACTION_TAKEN"

    db.commit()

    return {
        "message": "Action recorded successfully",
        "status": notification.status,
        "action_taken_at": notification.action_taken_at.isoformat()
    }
