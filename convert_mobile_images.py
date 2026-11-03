from pathlib import Path
from PIL import Image

folder = Path(r"D:\Kaspersky\Usb Drive\AI-Surveillance-backend\dataset\mobile")

for name in ["mobile15.jpg", "mobile19.jpg"]:
    src = folder / name
    backup = folder / (name + ".original")

    if not backup.exists():
        backup.write_bytes(src.read_bytes())

    with Image.open(src) as im:
        converted = im.convert("RGB")
        converted.save(src, format="JPEG", quality=95)

    print(f"{name}: converted to JPEG. Backup: {backup.name}")
