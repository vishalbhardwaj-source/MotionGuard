import json
from pathlib import Path

events_path = Path("outputs/interaction_events_test.jsonl")
evidence_dir = Path("outputs/event_evidence_test")

with events_path.open(encoding="utf-8") as file:
    event_ids = {
        json.loads(line)["event_id"]
        for line in file
        if line.strip()
    }

stale_images = sorted(
    path.name
    for path in evidence_dir.glob("*.jpg")
    if path.stem not in event_ids
)

print(f"Stale evidence images: {len(stale_images)}")
for name in stale_images:
    print(name)
