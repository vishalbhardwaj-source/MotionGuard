import json
from pathlib import Path
from src.interaction_analysis import bbox_iou

path = Path("outputs/trajectories_trails_test.jsonl")
tracks = {}

with path.open(encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        if record["track_id"] in (422, 429):
            tracks.setdefault(record["track_id"], {})[
                record["timestamp_seconds"]
            ] = record

first = tracks.get(422, {})
second = tracks.get(429, {})
common = sorted(first.keys() & second.keys())

matches = []
for timestamp in common:
    overlap = bbox_iou(
        first[timestamp].get("bbox_xyxy"),
        second[timestamp].get("bbox_xyxy"),
    )
    if overlap is not None and overlap >= 0.50:
        matches.append((timestamp, overlap))

print("Shared timestamps:", len(common))
print("Matches with IoU >= 0.50:", len(matches))
print("Matching timestamps and IoU:")
for timestamp, overlap in matches:
    print(f"  {timestamp:.3f}s | {overlap:.3f}")
