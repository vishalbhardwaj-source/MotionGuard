#!/usr/bin/env python3
"""
MotionGuard Model Weight Downloader
Downloads official YOLO11n weights from Ultralytics releases if not already cached.
"""

from pathlib import Path
from ultralytics import YOLO

WEIGHTS_FILE = Path("yolo11n.pt")


def ensure_weights(target_path=WEIGHTS_FILE):
    path = Path(target_path)
    if path.is_file() and path.stat().st_size > 1000000:
        print(f"Weights already present at {path.resolve()} ({path.stat().st_size / (1024*1024):.2f} MB)")
        return str(path)

    print(f"Downloading YOLO11n weights to {path}...")
    model = YOLO("yolo11n.pt")
    print("YOLO11n weights successfully verified.")
    return str(path)


if __name__ == "__main__":
    ensure_weights()
