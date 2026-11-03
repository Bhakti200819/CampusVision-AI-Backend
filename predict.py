from ultralytics import YOLO
from datetime import datetime
import os
import shutil
import glob

# ===========================
# Load Trained Model
# ===========================
model = YOLO("runs/detect/runs/weapon_detection-3/weights/best.pt")

# ===========================
# Detect Image
# ===========================
results = model.predict(
    source="test.jpg",
    conf=0.30,
    save=True,
    show=False
)

print("\n==============================")

weapon_detected = False

for result in results:
    boxes = result.boxes

    if len(boxes) == 0:
        print("✅ SAFE")
        print("No Weapon Detected")

    else:
        weapon_detected = True

        for box in boxes:
            cls = int(box.cls[0])
            name = model.names[cls]
            conf = float(box.conf[0])

            print("🚨 ALERT 🚨")
            print(f"Weapon : {name}")
            print(f"Confidence : {conf:.2f}")

            if name == "gun":
                print("Threat Level : 🔴 CRITICAL")

            elif name == "knife":
                print("Threat Level : 🟠 HIGH")

            now = datetime.now()
            print("Date :", now.strftime("%d-%m-%Y"))
            print("Time :", now.strftime("%I:%M:%S %p"))

print("==============================")

# ===========================
# Evidence Save
# ===========================

if weapon_detected:

    os.makedirs("evidence", exist_ok=True)

    predict_folders = glob.glob("runs/detect/predict*")

    latest_folder = max(predict_folders, key=os.path.getmtime)

    output_image = os.path.join(latest_folder, "test.jpg")

    if os.path.exists(output_image):

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"

        shutil.copy(
            output_image,
            os.path.join("evidence", filename)
        )

        print("📸 Evidence Saved Successfully!")

    else:
        print("❌ Output Image Not Found!")

print("✅ Detection Completed!")