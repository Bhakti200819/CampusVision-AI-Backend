
from fastapi import APIRouter

router = APIRouter()


@router.get("/cameras/status")
def camera_status():
    return {
        "status": "API Running",
        "camera_connected": False,
        "message": "Camera integration is pending"
    }


@router.post("/cameras/start")
def start_camera():
    return {
        "status": "pending",
        "message": "Connect classroom camera to start live detection"
    }


@router.get("/cameras")
def get_cameras():
    return {
        "total_cameras": 0,
        "cameras": []
    }
