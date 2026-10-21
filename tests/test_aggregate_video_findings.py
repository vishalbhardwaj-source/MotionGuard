
import json
from pathlib import Path

from src.event_aggregation import aggregate_interaction_events


INPUT_PATH = Path("outputs/interaction_findings_test.jsonl")
OUTPUT_PATH = Path("outputs/interaction_events_test.jsonl")


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_PATH}. Run test_interaction_from_video.py first."
        )

    findings = []

    with INPUT_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                findings.append(json.loads(line))

    events = aggregate_interaction_events(
        findings,
        max_gap_seconds=0.5,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    print("\nREAL-VIDEO AGGREGATION RESULTS")
    print("-" * 40)
    print(f"Raw interaction findings: {len(findings)}")
    print(f"Aggregated event episodes: {len(events)}")

    if findings:
        reduction = (1 - len(events) / len(findings)) * 100
        print(f"Reduction in repeated records: {reduction:.1f}%")

    print(f"\nSaved events to: {OUTPUT_PATH}")

    print("\nFIRST 10 EVENT EPISODES")
    print("-" * 40)

    for event in events[:10]:
        print(
            f"{event['event_id']} | "
            f"{event['start_seconds']:.2f}s–"
            f"{event['end_seconds']:.2f}s | "
            f"Tracks: {event['track_ids']} | "
            f"Detections: {event['detection_count']} | "
            f"Min distance: {event['minimum_distance_px']} px | "
            f"Peak closing speed: "
            f"{event['peak_closing_speed_px_per_second']} px/s"
        )


if __name__ == "__main__":
    main()
