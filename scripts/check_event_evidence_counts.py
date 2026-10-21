import json
from pathlib import Path

events_path = Path("outputs/interaction_events_test.jsonl")
evidence_dir = Path("outputs/event_evidence_test")

with events_path.open(encoding="utf-8") as file:
    events = [json.loads(line) for line in file if line.strip()]

event_ids = {event["event_id"] for event in events}
image_ids = {
    path.stem
    for path in evidence_dir.glob("*.jpg")
}

print("Event records:", len(events))
print("Unique event IDs:", len(event_ids))
print("Evidence JPGs:", len(image_ids))
print("Events without evidence:", len(event_ids - image_ids))
print("Evidence without an event:", len(image_ids - event_ids))
print("First event ID:", min(event_ids) if event_ids else "None")
print("Last event ID:", max(event_ids) if event_ids else "None")
