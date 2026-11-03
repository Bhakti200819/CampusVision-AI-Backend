
from pathlib import Path
import uuid

import cv2
from ultralytics import YOLO


# Model paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

PERSON_MODEL_PATH = PROJECT_ROOT / "models" / "yolov8n.pt"
MOBILE_MODEL_PATH = PROJECT_ROOT / "models" / "mobile_best.pt"

person_model = YOLO(str(PERSON_MODEL_PATH))
mobile_model = YOLO(str(MOBILE_MODEL_PATH))


# Detection thresholds
PERSON_THRESHOLD = 0.40
MOBILE_THRESHOLD = 0.25


# Output folders
APP_DIR = PROJECT_ROOT / "app"

OUTPUT_FOLDER = APP_DIR / "outputs"
STUDENT_CROP_FOLDER = APP_DIR / "student_crops"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
STUDENT_CROP_FOLDER.mkdir(parents=True, exist_ok=True)


def detect_mobile(image_path):
    image = cv2.imread(str(image_path))

    if image is None:
        return None

    height, width = image.shape[:2]

    # Detect people
    person_results = person_model.predict(
        source=image,
        classes=[0],
        conf=PERSON_THRESHOLD,
        verbose=False,
    )

    # Detect mobile phones
    mobile_results = mobile_model.predict(
        source=image,
        conf=MOBILE_THRESHOLD,
        iou=0.30,
        max_det=20,
        verbose=False,
    )

    persons = []
    mobile_candidates = []

    # Collect person boxes
    for box in person_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))

        if x2 <= x1 or y2 <= y1:
            continue

        persons.append({
            "box": (x1, y1, x2, y2),
            "confidence": float(box.conf[0]),
        })

    # Collect mobile phone boxes
    for box in mobile_results[0].boxes:
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])

        if class_id != 0 or confidence < MOBILE_THRESHOLD:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))

        if x2 <= x1 or y2 <= y1:
            continue

        mobile_candidates.append({
            "box": (x1, y1, x2, y2),
            "confidence": confidence,
        })

    annotated = image.copy()
    detections = []
    confirmed_mobiles = []

    # Match mobile phones to people by phone-box centre
    for mobile in mobile_candidates:
        mx1, my1, mx2, my2 = mobile["box"]

        mobile_cx = (mx1 + mx2) / 2
        mobile_cy = (my1 + my2) / 2

        matching_persons = []

        for person in persons:
            px1, py1, px2, py2 = person["box"]

            if px1 <= mobile_cx <= px2 and py1 <= mobile_cy <= py2:
                matching_persons.append(person)

        if matching_persons:
            matched_person = min(
                matching_persons,
                key=lambda p: (
                    (p["box"][2] - p["box"][0])
                    * (p["box"][3] - p["box"][1])
                ),
            )

            confirmed_mobiles.append((mobile, matched_person))

    # Draw detections and save student crops
    for student_id, (mobile, person) in enumerate(
        confirmed_mobiles, start=1
    ):
        mx1, my1, mx2, my2 = mobile["box"]
        px1, py1, px2, py2 = person["box"]

        padding_x = int((px2 - px1) * 0.08)
        padding_y = int((py2 - py1) * 0.08)

        crop_x1 = max(0, px1 - padding_x)
        crop_y1 = max(0, py1 - padding_y)
        crop_x2 = min(width, px2 + padding_x)
        crop_y2 = min(height, py2 + padding_y)

        student_crop = image[
            crop_y1:crop_y2,
            crop_x1:crop_x2,
        ]

        student_image_url = None

        if student_crop.size > 0:
            crop_filename = (
                f"student_{student_id}_{uuid.uuid4().hex[:8]}.jpg"
            )
            crop_path = STUDENT_CROP_FOLDER / crop_filename

            if cv2.imwrite(str(crop_path), student_crop):
                student_image_url = f"/app/student_crops/{crop_filename}"

        # Person bounding box
        cv2.rectangle(
            annotated,
            (px1, py1),
            (px2, py2),
            (255, 0, 0),
            2,
        )

        cv2.putText(
            annotated,
            f"Person {student_id}",
            (px1, max(py1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2,
        )

        # Mobile bounding box
        cv2.rectangle(
            annotated,
            (mx1, my1),
            (mx2, my2),
            (0, 0, 255),
            2,
        )

        confidence_percent = round(mobile["confidence"] * 100, 2)

        cv2.putText(
            annotated,
            f"Mobile {confidence_percent}%",
            (mx1, max(my1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )

        detections.append({
            "student_id": student_id,
            "mobile_detected": True,
            "confidence": confidence_percent,
            "student_image": student_image_url,
        })

    # Detection status
    mobile_detected = len(detections) > 0

    if mobile_detected:
        message = "MOBILE PHONE DETECTED"
        colour = (0, 0, 255)
    else:
        message = "NO MOBILE PHONE DETECTED"
        colour = (0, 255, 0)

    cv2.putText(
        annotated,
        message,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        colour,
        2,
    )

    # Save processed output image
    output_filename = f"mobile_output_{uuid.uuid4().hex[:8]}.jpg"
    output_path = OUTPUT_FOLDER / output_filename

    if not cv2.imwrite(str(output_path), annotated):
        return None

    # Return browser-accessible URLs, not local filesystem paths
    return {
        "message": message,
        "mobile_detected": mobile_detected,
        "mobile_count": len(detections),
        "student_count": len(persons),
        "detections": detections,
        "output_image": f"/outputs/{output_filename}",
    }
