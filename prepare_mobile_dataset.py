from pathlib import Path
from shutil import copy2
import random
import yaml

base = Path(r"D:\Kaspersky\Usb Drive\AI-Surveillance-backend\dataset")
images_dir = base / "mobile"
labels_dir = base / "mobile_labels"
out = base / "mobile_yolo"

extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
images = sorted(
    [p for p in images_dir.iterdir()
     if p.is_file() and p.suffix.lower() in extensions],
    key=lambda p: p.name.lower()
)

if not images:
    raise SystemExit("No images found.")

for image in images:
    label = labels_dir / (image.stem + ".txt")
    if not label.exists():
        raise SystemExit(f"Missing label: {label}")

# Negative image should be included in training.
negative = [p for p in images if p.stem.lower() == "no mobile"]
positive = [p for p in images if p.stem.lower() != "no mobile"]

random.Random(42).shuffle(positive)

n_train = round(len(positive) * 0.75)
n_val = round(len(positive) * 0.15)

splits = {
    "train": positive[:n_train] + negative,
    "val": positive[n_train:n_train+n_val],
    "test": positive[n_train+n_val:]
}

for split, files in splits.items():
    (out / split / "images").mkdir(parents=True, exist_ok=True)
    (out / split / "labels").mkdir(parents=True, exist_ok=True)

    for image in files:
        copy2(image, out / split / "images" / image.name)
        copy2(labels_dir / (image.stem + ".txt"),
              out / split / "labels" / (image.stem + ".txt"))

data = {
    "path": str(out).replace("\\", "/"),
    "train": "train/images",
    "val": "val/images",
    "test": "test/images",
    "names": {0: "mobile"}
}

with (out / "data.yaml").open("w", encoding="utf-8") as f:
    yaml.safe_dump(data, f, sort_keys=False)

print("Mobile dataset created:", out)
for split, files in splits.items():
    print(f"{split}: {len(files)} images")
print("Config:", out / "data.yaml")
print("Original images and weapon dataset were not modified.")
