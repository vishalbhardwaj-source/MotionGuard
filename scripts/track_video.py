import cv2
import torch
from pathlib import Path
from ultralytics import YOLO

video_path = Path("data/videos/normal.mp4")
output_path = Path("outputs/tracked_normal.mp4")

output_path.parent.mkdir(parents=True, exist_ok=True)

if not video_path.exists():
    raise FileNotFoundError(f"Video not found: {video_path}")

print("CUDA available:", torch.cuda.is_available())

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(str(video_path))

if not cap.isOpened():
    raise RuntimeError("Could not open input video.")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

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
frames_with_tracks = 0
track_ids_seen = set()

try:
    while True:
        success, frame = cap.read()

        if not success:
            break

        result = model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            device=0,
            conf=0.25,
            verbose=False,
        )[0]

        annotated_frame = result.plot()

        if result.boxes is not None and result.boxes.id is not None:
            ids = result.boxes.id.int().cpu().tolist()
            track_ids_seen.update(ids)

            if ids:
                frames_with_tracks += 1

        writer.write(annotated_frame)
        frame_number += 1

        if frame_number % 100 == 0:
            print(f"Tracked {frame_number} frames")

finally:
    cap.release()
    writer.release()

print("\nTracking complete.")
print("Frames processed:", frame_number)
print("Frames containing tracked objects:", frames_with_tracks)
print("Distinct track IDs observed:", len(track_ids_seen))
print("Output:", output_path)