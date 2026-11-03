from fastapi import APIRouter, UploadFile, File
import shutil
import os

from app.services.weapon_service import detect_weapon
from app.services.weapon_service import detect_video_weapon

router = APIRouter()

UPLOAD_FOLDER = "app/uploads"

@router.post("/detect")
async def detect(file: UploadFile = File(...)):


    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = detect_weapon(file_path)

    return {
        "message": "Weapon Detection Completed",
        "weapon": result["weapon"],
        "confidence": result["confidence"],
        "output_image": result["output_image"]
    }
@router.post("/detect-video")
async def detect_video(file: UploadFile = File(...)):
    return await detect_video_weapon(file)