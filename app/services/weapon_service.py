from ultralytics import YOLO
import cv2
import os
from fastapi import UploadFile

MODEL_PATH = os.path.join("models", "weapon.pt")

model = YOLO(MODEL_PATH)

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("app/outputs", exist_ok=True)


# ==========================
# IMAGE DETECTION
# ==========================
def detect_weapon(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return None

    results = model(image)

    alarm = False

    if len(results[0].boxes) > 0:
        for box in results[0].boxes:
            conf = float(box.conf[0])

            if conf > 0.60:
                alarm = True
                break

    annotated = results[0].plot()

    if alarm:
        cv2.putText(
            annotated,
            "!!! WEAPON DETECTED !!!",
            (40, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.3,
            (0, 0, 255),
            3
        )

    output_path = os.path.join("app", "outputs", "output.jpg")
    cv2.imwrite(output_path, annotated)

    weapon = "No Weapon"
    confidence = 0

    if len(results[0].boxes) > 0:
        box = results[0].boxes[0]
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        weapon = model.names[class_id]

    return {
        "weapon": weapon,
        "confidence": round(confidence * 100, 2),
        "output_image": output_path
    }


# ==========================
# VIDEO DETECTION
# ==========================
async def detect_video_weapon(file: UploadFile):

    upload_path = f"uploads/{file.filename}"

    with open(upload_path, "wb") as buffer:
        buffer.write(await file.read())

    output_path = f"outputs/{file.filename}"

    cap = cv2.VideoCapture(upload_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    out = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        results = model(frame)

        alarm = False

        if len(results[0].boxes) > 0:
            for box in results[0].boxes:
                conf = float(box.conf[0])

                if conf > 0.60:
                    alarm = True
                    break

        annotated = results[0].plot()

        if alarm:
            cv2.putText(
                annotated,
                "!!! WEAPON DETECTED !!!",
                (40, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.3,
                (0, 0, 255),
                3
            )

        out.write(annotated)

    cap.release()
    out.release()

    return {
        "message": "Video processed successfully",
        "video": output_path
    }
