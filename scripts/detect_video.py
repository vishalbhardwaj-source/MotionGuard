import cv2
import torch
from pathlib import Path
from ultralytics import YOLO

video_path = Path("data/videos/normal.mp4")
output_path = Path("outputs/annotated_normal.mp4")

if not video_path.exists():
    raise FileNotFoundError(f"Video not found: {video_path}")

output_path.parent.mkdir(parents=True, exist_ok=True)

print("CUDA available:", torch.cuda.is_available())

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(str(video_path))

if not cap.isOpened():
    raise RuntimeError("Could not open input video.")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

writer = cv2.VideoWriter(
    str(output_path),
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps if fps > 0 else 30,
    (width, height),
)

if not writer.isOpened():
    cap.release()
    raise RuntimeError("Could not create output video.")

frame_number = 0
frames_with_detections = 0
total_detections = 0

try:
    while True:
        success, frame = cap.read()

        if not success:
            break

        # Process every second frame to start.
        if frame_number % 2 == 0:
            result = model.predict(
                source=frame,
                device=0,
                conf=0.25,
                verbose=False,
            )[0]

            annotated_frame = result.plot()
            count = len(result.boxes)

            total_detections += count

            if count:
                frames_with_detections += 1
        else:
            # Keep the video continuous between inference frames.
            annotated_frame = frame

        writer.write(annotated_frame)
        frame_number += 1

        if frame_number % 100 == 0:
            print(f"Processed {frame_number}/{total_frames} frames")

finally:
    cap.release()
    writer.release()

print("\nVideo processing complete.")
print("Frames processed:", frame_number)
print("Frames with detections:", frames_with_detections)
print("Total detections across sampled frames:", total_detections)
print("Output:", output_path)