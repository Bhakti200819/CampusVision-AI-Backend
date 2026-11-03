
from ultralytics import YOLO
import cv2
import os
import uuid
import math


MODEL_PATH = os.path.join("models", "yolov8n.pt")

model = YOLO(MODEL_PATH)

PERSON_THRESHOLD = 0.40
MOBILE_THRESHOLD = 0.20

OUTPUT_FOLDER = os.path.join("app", "outputs")
STUDENT_CROP_FOLDER = os.path.join("app", "student_crops")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(STUDENT_CROP_FOLDER, exist_ok=True)


def detect_mobile(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return None

    results = model.predict(
        source=image,
        conf=0.10,
        verbose=False
    )

    persons = []
    mobile_candidates = []

    height, width = image.shape[:2]

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = model.names[class_id]

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))

        if x2 <= x1 or y2 <= y1:
            continue

        if (
            class_name == "person"
            and confidence >= PERSON_THRESHOLD
        ):
            persons.append({
                "box": (x1, y1, x2, y2),
                "confidence": confidence
            })

        elif (
            class_name == "cell phone"
            and confidence >= MOBILE_THRESHOLD
        ):
            mobile_candidates.append({
                "box": (x1, y1, x2, y2),
                "confidence": confidence
            })

    annotated = image.copy()
    detections = []

    # Accept a phone candidate only if its centre lies
    # inside a detected person's bounding box.
    confirmed_mobiles = []

    for mobile in mobile_candidates:
        mx1, my1, mx2, my2 = mobile["box"]

        mobile_cx = (mx1 + mx2) / 2
        mobile_cy = (my1 + my2) / 2

        matching_persons = []

        for person in persons:
            px1, py1, px2, py2 = person["box"]

            if (
                px1 <= mobile_cx <= px2
                and py1 <= mobile_cy <= py2
            ):
                matching_persons.append(person)

        if matching_persons:
            # Choose the smallest containing person box
            # when more than one person overlaps.
            nearest_person = min(
                matching_persons,
                key=lambda p: (
                    (p["box"][2] - p["box"][0])
                    * (p["box"][3] - p["box"][1])
                )
            )

            confirmed_mobiles.append(
                (mobile, nearest_person)
            )

    for student_id, (mobile, person) in enumerate(
        confirmed_mobiles,
        start=1
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
            crop_x1:crop_x2
        ]

        crop_path = None

        if student_crop.size > 0:
            crop_filename = (
                f"student_{student_id}_"
                f"{uuid.uuid4().hex[:8]}.jpg"
            )

            crop_path = os.path.join(
                STUDENT_CROP_FOLDER,
                crop_filename
            )

            if not cv2.imwrite(crop_path, student_crop):
                crop_path = None

        # Person box: blue
        cv2.rectangle(
            annotated,
            (px1, py1),
            (px2, py2),
            (255, 0, 0),
            2
        )

        cv2.putText(
            annotated,
            f"Person {student_id}",
            (px1, max(py1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )

        # Phone box: red
        cv2.rectangle(
            annotated,
            (mx1, my1),
            (mx2, my2),
            (0, 0, 255),
            2
        )

        confidence_percent = round(
            mobile["confidence"] * 100,
            2
        )

        cv2.putText(
            annotated,
            f"Mobile {confidence_percent}%",
            (mx1, max(my1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2
        )

        detections.append({
            "student_id": student_id,
            "mobile_detected": True,
            "confidence": confidence_percent,
            "student_image": crop_path
        })

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
        2
    )

    output_filename = (
        f"mobile_output_{uuid.uuid4().hex[:8]}.jpg"
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        output_filename
    )

    if not cv2.imwrite(output_path, annotated):
        return None

    return {
        "mobile_detected": mobile_detected,
        "mobile_count": len(detections),
        "student_count": len(persons),
        "detections": detections,
        "output_image": output_path
    }
