import cv2
from pathlib import Path

BASE = Path(r"D:\Kaspersky\Usb Drive\AI-Surveillance-backend\dataset\mobile")
OUT = BASE.parent / "mobile_labels"
OUT.mkdir(parents=True, exist_ok=True)

extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
images = sorted(
    [p for p in BASE.iterdir()
     if p.is_file() and p.suffix.lower() in extensions],
    key=lambda p: p.name.lower()
)

if not images:
    raise SystemExit(f"No images found in: {BASE}")

index = 0
boxes = []
current_image = None
drawing = False
start_point = None
preview = None

def mouse(event, x, y, flags, param):
    global drawing, start_point, boxes, preview

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        preview = (x, y)

    elif event == cv2.EVENT_LBUTTONUP and drawing:
        drawing = False
        x1, y1 = start_point
        x2, y2 = x, y
        x1, x2 = sorted([max(0, min(x1, current_image.shape[1]-1)),
                         max(0, min(x2, current_image.shape[1]-1))])
        y1, y2 = sorted([max(0, min(y1, current_image.shape[0]-1)),
                         max(0, min(y2, current_image.shape[0]-1))])
        if x2 - x1 >= 3 and y2 - y1 >= 3:
            boxes.append((x1, y1, x2, y2))
        preview = None

cv2.namedWindow("Mobile Annotation", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Mobile Annotation", mouse)

while index < len(images):
    path = images[index]
    current_image = cv2.imread(str(path))

    if current_image is None:
        print("Cannot read:", path.name)
        index += 1
        continue

    label_path = OUT / (path.stem + ".txt")
    if not boxes and label_path.exists():
        lines = label_path.read_text().strip().splitlines()
        for line in lines:
            try:
                cls, xc, yc, w, h = map(float, line.split())
                H, W = current_image.shape[:2]
                x1 = int((xc - w/2) * W)
                y1 = int((yc - h/2) * H)
                x2 = int((xc + w/2) * W)
                y2 = int((yc + h/2) * H)
                boxes.append((x1, y1, x2, y2))
            except ValueError:
                pass

    while True:
        display = current_image.copy()
        H, W = display.shape[:2]

        for j, (x1, y1, x2, y2) in enumerate(boxes):
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(display, "mobile", (x1, max(20, y1-8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if drawing and preview:
            cv2.rectangle(display, start_point, preview, (0, 255, 255), 2)

        message = f"{index+1}/{len(images)}: {path.name} | Boxes: {len(boxes)}"
        cv2.putText(display, message, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(display, "Draw box | S=save/next | U=undo | N=skip | Q=quit",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        cv2.imshow("Mobile Annotation", display)
        key = cv2.waitKey(20) & 0xFF

        if key == ord("u") and boxes:
            boxes.pop()

        elif key == ord("s"):
            if path.stem.lower() == "no mobile":
                label_path.write_text("", encoding="utf-8")
                print("Saved negative image:", path.name)
            elif boxes:
                rows = []
                for x1, y1, x2, y2 in boxes:
                    xc = ((x1 + x2) / 2) / W
                    yc = ((y1 + y2) / 2) / H
                    bw = (x2 - x1) / W
                    bh = (y2 - y1) / H
                    rows.append(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
                label_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
                print("Saved:", label_path.name)
            else:
                print("Draw a box around the mobile before saving.")
                continue

            boxes = []
            index += 1
            break

        elif key == ord("n"):
            boxes = []
            index += 1
            break

        elif key == ord("q"):
            cv2.destroyAllWindows()
            raise SystemExit("Stopped. Saved labels are preserved.")

    if index < len(images):
        next_path = images[index]
        next_label = OUT / (next_path.stem + ".txt")
        if next_label.exists():
            try:
                current_lines = next_label.read_text().strip().splitlines()
                current_image = cv2.imread(str(next_path))
                boxes = []
                if current_image is not None:
                    H, W = current_image.shape[:2]
                    for line in current_lines:
                        cls, xc, yc, w, h = map(float, line.split())
                        boxes.append((int((xc-w/2)*W), int((yc-h/2)*H),
                                      int((xc+w/2)*W), int((yc+h/2)*H)))
            except (ValueError, OSError):
                boxes = []
        else:
            boxes = []

cv2.destroyAllWindows()
print("Annotation session finished.")
print("Labels folder:", OUT)
