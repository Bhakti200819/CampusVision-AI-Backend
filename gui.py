import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from ultralytics import YOLO
from datetime import datetime
import os
import shutil
import glob
import csv

# ==========================================
# AI SECURITY SURVEILLANCE SYSTEM
# Weapon Detection Module
# ==========================================

# Load Trained YOLO Model
model = YOLO("runs/detect/runs/weapon_detection-3/weights/best.pt")

# Global Variables
image_path = ""
detected_photo = None
original_photo = None

# Create folders if they don't exist
os.makedirs("evidence", exist_ok=True)
os.makedirs("history", exist_ok=True)

# Create history file if it doesn't exist
history_file = "history/history.csv"

if not os.path.exists(history_file):
    with open(history_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Date",
            "Time",
            "Weapon",
            "Confidence",
            "Threat Level"
        ])
# ==========================================
# Upload Image Function
# ==========================================

def upload_image():

    global image_path
    global original_photo

    image_path = filedialog.askopenfilename(
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png")
        ]
    )

    if image_path == "":
        return

    try:

        img = Image.open(image_path)
        img = img.resize((350, 300))

        original_photo = ImageTk.PhotoImage(img)

        image_label.config(
            image=original_photo,
            text=""
        )

        image_label.image = original_photo

        # Clear previous detected image
        detected_image_label.config(
            image="",
            text="No Detection"
        )

        detected_image_label.image = None

        # Reset Result Panel
        weapon_label.config(text="Weapon : -")
        confidence_label.config(text="Confidence : -")
        threat_label.config(text="Threat Level : -", fg="black")
        date_label.config(text="Date : -")
        time_label.config(text="Time : -")

        status_label.config(
            text="✅ Image Loaded Successfully",
            fg="green"
        )

    except Exception as e:

        messagebox.showerror(
            "Image Error",
            f"Unable to open image.\n\n{e}"
        )

        image_path = ""
# ==========================================
# Detect Weapon Function
# ==========================================

def detect_weapon():

    global image_path
    global detected_photo

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

            weapon_label.config(
                text="Weapon : NONE"
            )

            confidence_label.config(
                text="Confidence : 0%"
            )

            threat_label.config(
                text="Threat Level : SAFE",
                fg="green"
            )

            date_label.config(
                text="Date : -"
            )

            time_label.config(
                text="Time : -"
            )

            status_label.config(
                text="✅ No Weapon Detected",
                fg="green"
            )

            messagebox.showinfo(
                "AI Security",
                "No Weapon Detected"
            )

            return

        weapon_found = True

        for box in boxes:

            cls = int(box.cls[0])

            weapon = model.names[cls]

            confidence = float(box.conf[0]) * 100

            if weapon.lower() == "gun":
                threat = "CRITICAL"
                color = "red"
            else:
                threat = "HIGH"
                color = "orange"

            now = datetime.now()

            weapon_label.config(
                text=f"Weapon : {weapon.upper()}"
            )

            confidence_label.config(
                text=f"Confidence : {confidence:.2f}%"
            )

            threat_label.config(
                text=f"Threat Level : {threat}",
                fg=color
            )

            date_label.config(
                text="Date : " +
                now.strftime("%d-%m-%Y")
            )

            time_label.config(
                text="Time : " +
                now.strftime("%I:%M:%S %p")
            )

            status_label.config(
                text="🚨 Weapon Detected!",
                fg="red"
            )

            messagebox.showwarning(
                "AI ALERT",
                f"{weapon.upper()} Detected!"
            )
            # ==========================================
            # SAVE EVIDENCE
            # ==========================================

            predict_folders = glob.glob("runs/detect/predict*")

            if predict_folders:

                latest_folder = max(
                    predict_folders,
                    key=os.path.getmtime
                )

                output_image = os.path.join(
                    latest_folder,
                    os.path.basename(image_path)
                )

                if os.path.exists(output_image):

                    evidence_name = datetime.now().strftime(
                        "%Y-%m-%d_%H-%M-%S"
                    ) + ".jpg"

                    evidence_path = os.path.join(
                        "evidence",
                        evidence_name
                    )

                    shutil.copy(
                        output_image,
                        evidence_path
                    )

                    print("📸 Evidence Saved")

                    # ==========================================
                    # SAVE HISTORY
                    # ==========================================

                    with open(
                        history_file,
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

                    print("📄 History Saved")

                    # ==========================================
                    # SHOW DETECTED IMAGE
                    # ==========================================

                    detected_img = Image.open(output_image)
                    detected_img = detected_img.resize((350, 300))

                    detected_photo = ImageTk.PhotoImage(
                        detected_img
                    )

                    detected_image_label.config(
                        image=detected_photo,
                        text=""
                    )

                    detected_image_label.image = detected_photo
def view_history():


    if not os.path.exists(history_file):
        messagebox.showinfo(
            "History",
            "No Detection History Found."
        )
        return

    history_window = tk.Toplevel(root)
    history_window.title("Detection History")
    history_window.geometry("700x400")

    tree = ttk.Treeview(
        history_window,
        columns=("Date","Time","Weapon","Confidence","Threat"),
        show="headings"
    )

    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")
    tree.heading("Weapon", text="Weapon")
    tree.heading("Confidence", text="Confidence")
    tree.heading("Threat", text="Threat")

    tree.column("Date", width=100)
    tree.column("Time", width=120)
    tree.column("Weapon", width=120)
    tree.column("Confidence", width=120)
    tree.column("Threat", width=120)

    tree.pack(fill="both", expand=True)

    with open(history_file, "r", encoding="utf-8") as file:

        reader = csv.reader(file)

        next(reader)

        for row in reader:
            tree.insert("", tk.END, values=row)

def clear_all():

    global image_path

    image_path = ""

    image_label.config(
        image="",
        text="No Image Selected"
    )

    detected_image_label.config(
        image="",
        text="No Detection"
    )

    image_label.image = None
    detected_image_label.image = None

    weapon_label.config(text="Weapon : -")
    confidence_label.config(text="Confidence : -")
    threat_label.config(text="Threat Level : -", fg="black")
    date_label.config(text="Date : -")
    time_label.config(text="Time : -")

    status_label.config(
        text="Waiting for Image...",
        fg="blue"
    )

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
    text="📁 Upload Image",
    width=18,
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
    command=upload_image
)

upload_btn.grid(row=0, column=0, padx=10)

detect_btn = tk.Button(
    button_frame,
    text="🔍 Detect Weapon",
    width=18,
    font=("Arial", 12, "bold"),
    bg="#E53935",
    fg="white",
    command=detect_weapon
)

detect_btn.grid(row=0, column=1, padx=10)
history_btn = tk.Button(
    button_frame,
    text="📜 View History",
    width=18,
    font=("Arial",12,"bold"),
    bg="#1976D2",
    fg="white",
    command=view_history
)

history_btn.grid(row=0, column=2, padx=10)

clear_btn = tk.Button(
    button_frame,
    text="🧹 Clear",
    width=18,
    font=("Arial",12,"bold"),
    bg="#616161",
    fg="white",
    command=clear_all
)

clear_btn.grid(row=0, column=3, padx=10)


# ==========================================
# IMAGE SECTION
# ==========================================

image_frame = tk.Frame(root)
image_frame.pack(pady=10)

tk.Label(
    image_frame,
    text="Original Image",
    font=("Arial", 12, "bold")
).grid(row=0, column=0, padx=30)

tk.Label(
    image_frame,
    text="Detected Image",
    font=("Arial", 12, "bold")
).grid(row=0, column=1, padx=30)

image_label = tk.Label(
    image_frame,
    width=350,
    height=300,
    relief="solid",
    bd=2,
    text="No Image Selected"
)

image_label.grid(row=1, column=0, padx=20)

detected_image_label = tk.Label(
    image_frame,
    width=350,
    height=300,
    relief="solid",
    bd=2,
    text="No Detection"
)

detected_image_label.grid(row=1, column=1, padx=20)

# ==========================================
# STATUS LABEL
# ==========================================

status_label = tk.Label(
    root,
    text="Waiting for Image...",
    font=("Arial", 12, "bold"),
    fg="blue"
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
    font=("Arial", 12)
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
# START APPLICATION
# ==========================================

root.mainloop()