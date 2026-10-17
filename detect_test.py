from pathlib import Path
import torch
from ultralytics import YOLO

image_path = Path("outputs/evidence/test_frame.png")
output_dir = Path("outputs/evidence")

if not image_path.exists():
    raise FileNotFoundError(
        f"Image not found: {image_path}"
    )

print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))

print("Loading YOLO model...")
model = YOLO("yolo11n.pt")

print("Running detection...")
results = model.predict(
    source=str(image_path),
    device=0,
    conf=0.25,
    save=False,
    verbose=False,
)

result = results[0]
annotated = result.plot()

output_path = output_dir / "detection_test.jpg"

if not result.save(str(output_path)):
    raise RuntimeError("Could not save detection output.")

print("\nDetection complete!")
print("Objects detected:", len(result.boxes))
print("Saved:", output_path)

for box in result.boxes:
    class_id = int(box.cls[0].item())
    confidence = float(box.conf[0].item())
    name = model.names[class_id]
    print(f"{name}: {confidence:.2f}")