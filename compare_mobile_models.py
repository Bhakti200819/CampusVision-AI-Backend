from pathlib import Path
from ultralytics import YOLO

root = Path(__file__).resolve().parent
data = root / "dataset" / "mobile_yolo" / "val" / "images"

models = {
    "current": root / "models" / "mobile_best.pt",
    "v1": root / "runs" / "detect" / "runs" / "mobile_detection" / "mobile_v1" / "weights" / "best.pt",
    "v2": root / "runs" / "detect" / "runs" / "mobile_detection" / "mobile_v2-2" / "weights" / "best.pt",
    "finetune": root / "runs" / "detect" / "runs" / "mobile_detection" / "mobile_finetune_v1" / "weights" / "best.pt",
}

images = sorted(
    p for p in data.iterdir()
    if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
)

for name, model_path in models.items():
    print(f"\n--- {name}: {model_path.name} ---")
    if not model_path.exists():
        print("MODEL NOT FOUND")
        continue

    model = YOLO(str(model_path))
    for image in images:
        result = model.predict(
            source=str(image), conf=0.25, iou=0.30, verbose=False
        )[0]
        detections = [
            f"{result.names[int(box.cls[0])]}:{float(box.conf[0]):.2f}"
            for box in result.boxes
        ]
        print(f"{image.name}: {', '.join(detections) if detections else 'No detections'}")
