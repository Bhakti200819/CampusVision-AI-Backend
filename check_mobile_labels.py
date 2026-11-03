from pathlib import Path
import cv2

base = Path("dataset/mobile_yolo/test")
out = Path("runs/detect/label_check")
out.mkdir(parents=True, exist_ok=True)

for img_path in sorted((base / "images").glob("*")):
    img = cv2.imread(str(img_path))
    if img is None:
        print("Image read failed:", img_path.name)
        continue

    label_path = base / "labels" / (img_path.stem + ".txt")
    if label_path.exists():
        h, w = img.shape[:2]
        for line in label_path.read_text().splitlines():
            parts = line.split()
            if len(parts) != 5:
                continue
            _, xc, yc, bw, bh = map(float, parts)
            x1 = int((xc - bw / 2) * w)
            y1 = int((yc - bh / 2) * h)
            x2 = int((xc + bw / 2) * w)
            y2 = int((yc + bh / 2) * h)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    dest = out / img_path.name
    cv2.imwrite(str(dest), img)
    print("Saved:", dest)
