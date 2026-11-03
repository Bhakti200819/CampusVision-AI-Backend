
from ultralytics import YOLO
import cv2
import os

# AI Weapon Detection Model
model = YOLO("models/weapon.pt")


def detect_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25.0

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # AI Detection
            results = model(frame, verbose=False)
            annotated = results[0].plot()

            alarm = False
            weapon_name = ""
            confidence = 0.0

            for box in results[0].boxes:
                conf = float(box.conf[0])

                if conf > 0.60:
                    alarm = True
                    confidence = round(conf * 100, 1)

                    cls = int(box.cls[0])
                    weapon_name = model.names[cls]

                    break

            if alarm:
                cv2.rectangle(
                    annotated,
                    (15, 15),
                    (650, 100),
                    (0, 0, 180),
                    -1
                )

                cv2.putText(
                    annotated,
                    "SECURITY BREACH",
                    (30, 52),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    annotated,
                    f"{weapon_name.upper()}  {confidence}%",
                    (30, 85),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

            out.write(annotated)

    finally:
        cap.release()
        out.release()

    return output_path
