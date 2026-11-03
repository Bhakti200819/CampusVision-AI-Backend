import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, Depends
from app.auth_dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

# Storage location
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INCIDENTS_FILE = DATA_DIR / "incidents.json"


# Incident request model
class IncidentCreate(BaseModel):
    camera_id: str
    classroom: str
    detection_type: str = "Mobile Phone"
    confidence: Optional[float] = None
    mobile_image: Optional[str] = None
    face_snapshot: Optional[str] = None


# Read saved incidents
def read_incidents():
    if not INCIDENTS_FILE.exists():
        return []

    try:
        with open(INCIDENTS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


# Save incidents
def save_incidents(data):
    with open(INCIDENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# Get all detection history
@router.get("/incidents")
def get_incidents():
    return read_incidents()


# Create a new detection record
@router.post("/incidents")
def create_incident(incident: IncidentCreate):

    now = datetime.now().astimezone()

    record = {
        "incident_id": f"INC-{uuid4().hex[:8].upper()}",
        "camera_id": incident.camera_id,
        "classroom": incident.classroom,
        "detection_type": incident.detection_type,
        "confidence": incident.confidence,
        "mobile_image": incident.mobile_image,
        "face_snapshot": incident.face_snapshot,
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
        "time": now.strftime("%H:%M:%S"),
        "status": "OPEN"
    }

    incidents = read_incidents()
    incidents.insert(0, record)

    save_incidents(incidents)

    return {
        "message": "Detection record saved successfully",
        "incident": record
    }
