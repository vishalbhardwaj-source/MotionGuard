import json
from pathlib import Path

events_path = Path("outputs/interaction_events_test.jsonl")
evidence_dir = Path("outputs/event_evidence_test")

if not events_path.exists():
    raise FileNotFoundError(f"Events file missing: {events_path}")

if not evidence_dir.exists():
    raise FileNotFoundError(f"Evidence folder missing: {evidence_dir}")

with events_path.open(encoding="utf-8") as file:
    event_ids = {
        json.loads(line)["event_id"]
        for line in file
        if line.strip()
    }

stale_images = [
    path for path in evidence_dir.glob("*.jpg")
    if path.stem not in event_ids
]

print(f"Current event IDs: {len(event_ids)}")
print(f"Orphaned images found: {len(stale_images)}")

for path in stale_images:
    path.unlink()
    print(f"Deleted: {path.name}")

print(f"Remaining JPGs: {len(list(evidence_dir.glob('*.jpg')))}")
