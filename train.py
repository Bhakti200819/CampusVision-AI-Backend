from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="dataset/mobile_detection/data.yaml",
    epochs=100,
    imgsz=640,
    batch=8,
    workers=0,
    project="runs",
    name="mobile_detection"
)