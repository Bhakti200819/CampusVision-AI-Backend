import cv2
from pathlib import Path

base = Path(r"D:\Kaspersky\Usb Drive\AI-Surveillance-backend\dataset\mobile")
out = base.parent / "mobile_labels"
out.mkdir(exist_ok=True)

for name in ["mobile15.jpg", "mobile19.jpg"]:
    image_path = base / name
    image = cv2.imread(str(image_path))

    if image is None:
        print("Cannot read:", name)
        continue

    H, W = image.shape[:2]
    boxes = []
    start = None
    drawing = False
    preview = None

    def mouse(event, x, y, flags, param):
        global start, drawing, preview
        if event == cv2.EVENT_LBUTTONDOWN:
            start = (x, y)
            drawing = True
        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            preview = (x, y)
        elif event == cv2.EVENT_LBUTTONUP and drawing:
            x1, y1 = start
            x2, y2 = x, y
            x1, x2 = sorted([max(0, min(x1, W-1)), max(0, min(x2, W-1))])
            y1, y2 = sorted([max(0, min(y1, H-1)), max(0, min(y2, H-1))])
            if x2-x1 > 3 and y2-y1 > 3:
                boxes.append((x1, y1, x2, y2))
            drawing = False
            preview = None

    cv2.namedWindow("Label mobile", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Label mobile", mouse)

    while True:
        shown = image.copy()
        for x1, y1, x2, y2 in boxes:
            cv2.rectangle(shown, (x1,y1), (x2,y2), (0,255,0), 2)
        if drawing and preview:
            cv2.rectangle(shown, start, preview, (0,255,255), 2)
        cv2.putText(shown, f"{name} | Drag box; S=save, U=undo, Q=quit",
                    (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
        cv2.imshow("Label mobile", shown)
        key = cv2.waitKey(20) & 0xFF

        if key == ord("u") and boxes:
            boxes.pop()
        elif key == ord("s"):
            if not boxes:
                print("Draw a box first:", name)
                continue
            rows = []
            for x1,y1,x2,y2 in boxes:
                xc = ((x1+x2)/2)/W
                yc = ((y1+y2)/2)/H
                bw = (x2-x1)/W
                bh = (y2-y1)/H
                rows.append(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
            (out / (image_path.stem + ".txt")).write_text(
                "\n".join(rows) + "\n", encoding="utf-8"
            )
            print("Saved:", image_path.stem + ".txt")
            break
        elif key == ord("q"):
            cv2.destroyAllWindows()
            raise SystemExit("Stopped; saved labels are preserved.")

    cv2.destroyAllWindows()

print("Finished. Labels folder:", out)
