import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO
from datetime import datetime
import os
import shutil
import glob
import csv

# ==========================================
# LOAD MODEL
# ==========================================

model = YOLO("runs/detect/runs/weapon_detection-3/weights/best.pt")

image_path = ""

# ==========================================
# UPLOAD IMAGE
# ==========================================

def upload_image():

    global image_path

    image_path = filedialog.askopenfilename(
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png")
        ]
    )

    if image_path == "":
        return

    img = Image.open(image_path)
    img = img.resize((350, 300))

    photo = ImageTk.PhotoImage(img)

    image_label.config(image=photo)
    image_label.image = photo

    status_label.config(
        text="✅ Image Loaded Successfully",
        fg="green"
    )

# ==========================================
# DETECT WEAPON
# ==========================================

def detect_weapon():

    global image_path

    if image_path == "":
        messagebox.showwarning(
            "Warning",
            "Please Upload an Image First!"
        )
        return

    results = model.predict(
        source=image_path,
        conf=0.30,
        save=True,
        show=False
    )

    weapon_found = False
    for result in results:

        boxes = result.boxes

        if len(boxes) == 0:

            weapon_label.config(text="Weapon : None")
            confidence_label.config(text="Confidence : 0%")
            threat_label.config(
                text="Threat Level : SAFE",
                fg="green"
            )

            date_label.config(text="Date : -")
            time_label.config(text="Time : -")

            status_label.config(
                text="✅ No Weapon Detected",
                fg="green"
            )

        else:

            weapon_found = True

            for box in boxes:

                cls = int(box.cls[0])

                weapon = model.names[cls]

                confidence = float(box.conf[0]) * 100

                weapon_label.config(
                    text=f"Weapon : {weapon.upper()}"
                )

                confidence_label.config(
                    text=f"Confidence : {confidence:.2f}%"
                )

                if weapon == "gun":
                    threat = "CRITICAL"
                else:
                  threat = "HIGH"

threat_label.config(
                    text=f"Threat Level : {threat}",
                    fg="red"
                )

now = datetime.now()

date_label.config(
                    text="Date : " + now.strftime("%d-%m-%Y")
                )

time_label.config(
                    text="Time : " + now.strftime("%I:%M:%S %p")
                )

status_label.config(
                    text="🚨 Weapon Detected!",
                    fg="red"
                )

messagebox.showwarning(
                    "AI Alert",
                    f"{weapon.upper()} Detected!"
                )
                # ==========================================
                # SAVE EVIDENCE
                # ==========================================

os.makedirs("evidence", exist_ok=True)

predict_folders = glob.glob("runs/detect/predict*")

if predict_folders:

                    latest = max(
                        predict_folders,
                        key=os.path.getmtime
                    )

                    output_image = os.path.join(
                        latest,
                        os.path.basename(image_path)
                    )

                    if os.path.exists(output_image):

                        filename = datetime.now().strftime(
                            "%Y-%m-%d_%H-%M-%S"
                        ) + ".jpg"

                        shutil.copy(
                            output_image,
                            os.path.join(
                                "evidence",
                                filename
                            )
                        )

                        print("📸 Evidence Saved")

                        # ==========================================
                        # SAVE HISTORY
                        # ==========================================

                        os.makedirs("history", exist_ok=True)

                        with open(
    "history/history.csv",
    "a",
    newline="",
    encoding="utf-8"
) as file:

                            writer = csv.writer(file)

                            writer.writerow([
                                now.strftime("%d-%m-%Y"),
                                now.strftime("%I:%M:%S %p"),
                                weapon.upper(),
                                f"{confidence:.2f}%",
                                threat
                            ])

                        # ==========================================
                        # SHOW DETECTED IMAGE
                        # ==========================================

                        detected_img = Image.open(output_image)
                        detected_img = detected_img.resize((350, 300))

                        detected_photo = ImageTk.PhotoImage(
                            detected_img
                        )

                        detected_image_label.config(
                            image=detected_photo
                        )

                        detected_image_label.image = detected_photo
# ==========================================
# GUI WINDOW
# ==========================================

root = tk.Tk()

root.title("AI Security Surveillance System")
root.geometry("1050x720")
root.resizable(False, False)

# ==========================================
# TITLE
# ==========================================

title = tk.Label(
    root,
    text="AI SECURITY SURVEILLANCE SYSTEM",
    font=("Arial", 20, "bold"),
    fg="red"
)

title.pack(pady=10)

# ==========================================
# BUTTONS
# ==========================================

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

upload_btn = tk.Button(
    button_frame,
    text="Upload Image",
    width=18,
    font=("Arial", 12, "bold"),
    command=upload_image
)

upload_btn.grid(row=0, column=0, padx=10)

detect_btn = tk.Button(
    button_frame,
    text="Detect Weapon",
    width=18,
    font=("Arial", 12, "bold"),
    command=detect_weapon
)

detect_btn.grid(row=0, column=1, padx=10)

# ==========================================
# IMAGE SECTION
# ==========================================

image_frame = tk.Frame(root)
image_frame.pack(pady=10)

original_title = tk.Label(
    image_frame,
    text="Original Image",
    font=("Arial", 12, "bold")
)

original_title.grid(row=0, column=0, padx=30)

detected_title = tk.Label(
    image_frame,
    text="Detected Image",
    font=("Arial", 12, "bold")
)

detected_title.grid(row=0, column=1, padx=30)

image_label = tk.Label(
    image_frame,
    width=350,
    height=300,
    bd=2,
    relief="solid"
)

image_label.grid(row=1, column=0, padx=20)

detected_image_label = tk.Label(
    image_frame,
    width=350,
    height=300,
    bd=2,
    relief="solid"
)

detected_image_label.grid(row=1, column=1, padx=20)

# ==========================================
# STATUS
# ==========================================

status_label = tk.Label(
    root,
    text="Waiting for Image...",
    font=("Arial", 12)
)

status_label.pack(pady=10)
# ==========================================
# RESULT PANEL
# ==========================================

result_frame = tk.LabelFrame(
    root,
    text="Detection Result",
    font=("Arial", 12, "bold"),
    padx=15,
    pady=15
)

result_frame.pack(
    fill="x",
    padx=20,
    pady=15
)

weapon_label = tk.Label(
    result_frame,
    text="Weapon : -",
    font=("Arial", 12)
)

weapon_label.pack(anchor="w")

confidence_label = tk.Label(
    result_frame,
    text="Confidence : -",
    font=("Arial", 12)
)

confidence_label.pack(anchor="w")

threat_label = tk.Label(
    result_frame,
    text="Threat Level : -",
    font=("Arial", 12),
    fg="black"
)

threat_label.pack(anchor="w")

date_label = tk.Label(
    result_frame,
    text="Date : -",
    font=("Arial", 12)
)

date_label.pack(anchor="w")

time_label = tk.Label(
    result_frame,
    text="Time : -",
    font=("Arial", 12)
)

time_label.pack(anchor="w")

# ==========================================
# FOOTER
# ==========================================

footer = tk.Label(
    root,
    text="Developed by Bhakti | AI Security Surveillance System",
    font=("Arial", 10),
    fg="gray"
)

footer.pack(side="bottom", pady=8)
# ==========================================
# START GUI
# ==========================================

root.mainloop()