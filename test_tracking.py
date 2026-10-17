
import json
from pathlib import Path

from src.video_processor import track_video
from src.trajectory_analysis import analyze_trajectories


trajectory_path = Path("outputs/trajectories_integration_test.jsonl")

result = track_video(
    video_path="data/videos/normal.mp4",
    output_path="outputs/tracking_integration_test.mp4",
    trajectory_output_path=trajectory_path,
    progress_callback=lambda progress: print(
        f"Progress: {progress:.0%}"
    ),
)

records = [
    json.loads(line)
    for line in trajectory_path.read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]

analysis = analyze_trajectories(records)

valid_speeds = [
    item["image_speed_px_per_second"]
    for item in analysis
    if item["image_speed_px_per_second"] is not None
]

print("\nTracking test complete:")
print(result)

print("\nTrajectory analysis:")
print(f"Records exported: {len(records)}")
print(
    "Distinct tracked IDs:",
    len({item["track_id"] for item in records}),
)
print(f"Motion measurements: {len(valid_speeds)}")

if valid_speeds:
    print(
        "Average image-space speed:",
        f"{sum(valid_speeds) / len(valid_speeds):.2f} px/s",
    )

print("\nNote: image-space speed is not vehicle speed in km/h.")
