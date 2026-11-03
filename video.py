from fastapi import APIRouter, UploadFile, File
from app.services.video_service import detect_video
import shutil
import os

router = APIRouter(prefix="/video", tags=["Video"])

UPLOAD_FOLDER = "app/uploads/videos"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_folder = "app/outputs"
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, file.filename)

    detect_video(file_path, output_path)

    return {
        "message": "Video Weapon Detection Completed",
        "output_video": output_path
    }