import json
from pathlib import Path
from src.interaction_analysis import bbox_iou

path = Path("outputs/trajectories_trails_test.jsonl")
records = {}

with path.open(encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        if record["track_id"] in (422, 429):
            key = (record["track_id"], record["timestamp_seconds"])
            records[key] = record

times_422 = {t for track_id, t in records if track_id == 422}
times_429 = {t for track_id, t in records if track_id == 429}

for timestamp in sorted(times_422 & times_429):
    box_422 = records[(422, timestamp)].get("bbox_xyxy")
    box_429 = records[(429, timestamp)].get("bbox_xyxy")
    overlap = bbox_iou(box_422, box_429)
    print(f"{timestamp:.3f}s | IoU: {overlap}")
