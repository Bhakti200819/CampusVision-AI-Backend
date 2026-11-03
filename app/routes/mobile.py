
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.auth_dependencies import get_current_user
from pathlib import Path
import shutil
import uuid

from app.services.mobile_service import detect_mobile

router = APIRouter()

# Upload folder
BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@router.post("/detect")
async def detect(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):

    # Validate uploaded file
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was uploaded."
        )

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Upload a JPG, JPEG, PNG, or WEBP image."
        )

    # Generate a unique filename to avoid overwriting files
    filename = f"mobile_{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_FOLDER / filename

    try:
        # Save uploaded image
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run mobile detection
        result = detect_mobile(str(file_path))

        if result is None:
            raise HTTPException(
                status_code=422,
                detail="Unable to process image."
            )

        return {
            "message": "Mobile Detection Completed",
            "mobile_detected": result["mobile_detected"],
            "mobile_count": result["mobile_count"],
            "student_count": result["student_count"],
            "detections": result["detections"],
            "output_image": result["output_image"]
        }

    except HTTPException:
        raise

    except Exception as error:
        print(f"Mobile detection error: {error}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the image."
        )

    finally:
        await file.close()
