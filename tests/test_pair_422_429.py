import json
from pathlib import Path
from src.interaction_analysis import is_persistent_duplicate

path = Path("outputs/trajectories_trails_test.jsonl")
tracks = {}

with path.open(encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        track_id = record["track_id"]

        if track_id not in (422, 429):
            continue

        observation = {
            "timestamp": record["timestamp_seconds"],
            "bbox_xyxy": record.get("bbox_xyxy"),
        }
        tracks.setdefault(track_id, []).append(observation)

result = is_persistent_duplicate(
    tracks.get(422, []),
    tracks.get(429, []),
    {"car"},
    {"car"},
)

print("Track 422 observations:", len(tracks.get(422, [])))
print("Track 429 observations:", len(tracks.get(429, [])))
print("Flagged as persistent duplicate:", result)
