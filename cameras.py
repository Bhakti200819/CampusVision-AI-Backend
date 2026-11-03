
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from app.auth_dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CAMERA_FILE = DATA_DIR / "cameras.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

if not CAMERA_FILE.exists():
    CAMERA_FILE.write_text("[]", encoding="utf-8")


class Camera(BaseModel):
    id: str
    room: str
    zone: str
    type: str
    source: str = ""


def read_cameras():
    try:
        return json.loads(CAMERA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_cameras(cameras):
    CAMERA_FILE.write_text(
        json.dumps(cameras, indent=4),
        encoding="utf-8"
    )


@router.get("/cameras")
def get_cameras():
    return read_cameras()


@router.post("/cameras")
def register_camera(camera: Camera):
    cameras = read_cameras()

    if any(item["id"] == camera.id for item in cameras):
        raise HTTPException(
            status_code=409,
            detail="Camera ID already registered"
        )

    new_camera = {
        **camera.model_dump(),
        "status": "NOT CONFIGURED",
    }

    cameras.append(new_camera)
    save_cameras(cameras)

    return {
        "message": "Camera registered successfully",
        "camera": new_camera,
    }
@router.put("/cameras/{camera_id}")
def update_camera(camera_id: str, camera: Camera):
    cameras = read_cameras()

    current_index = next(
        (i for i, item in enumerate(cameras) if item["id"] == camera_id),
        None
    )

    if current_index is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    if any(
        item["id"] == camera.id and item["id"] != camera_id
        for item in cameras
    ):
        raise HTTPException(
            status_code=409,
            detail="New Camera ID already exists"
        )

    updated_camera = {
        **camera.model_dump(),
        "status": cameras[current_index].get(
            "status", "NOT CONFIGURED"
        ),
    }

    cameras[current_index] = updated_camera
    save_cameras(cameras)

    return {
        "message": "Camera updated successfully",
        "camera": updated_camera,
    }
def update_camera(camera_id: str, camera: Camera):
    cameras = read_cameras()

    for index, item in enumerate(cameras):
        if item["id"] == camera_id:
            updated_camera = {
                **camera.model_dump(),
                "status": item.get("status", "NOT CONFIGURED"),
            }

            cameras[index] = updated_camera
            save_cameras(cameras)

            return {
                "message": "Camera updated successfully",
                "camera": updated_camera,
            }

    raise HTTPException(
        status_code=404,
        detail="Camera not found"
    )
@router.delete("/cameras/{camera_id}")
def delete_camera(camera_id: str):
    cameras = read_cameras()

    camera_index = next(
        (
            index
            for index, item in enumerate(cameras)
            if item["id"] == camera_id
        ),
        None
    )

    if camera_index is None:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )

    deleted_camera = cameras.pop(camera_index)
    save_cameras(cameras)

    return {
        "message": "Camera deleted successfully",
        "camera": deleted_camera
    }