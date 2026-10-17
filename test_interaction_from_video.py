
import json
from pathlib import Path

from src.interaction_analysis import analyze_interactions


INPUT_PATH = Path("outputs/trajectories_trails_test.jsonl")
OUTPUT_PATH = Path("outputs/interaction_findings_test.jsonl")


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Trajectory file not found: {INPUT_PATH}"
        )

    records = []

    with INPUT_PATH.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            bbox = record.get("bbox_xyxy")

            if not isinstance(bbox, list) or len(bbox) != 4:
                raise ValueError(
                    f"Invalid bbox_xyxy on line {line_number}"
                )

            x1, y1, x2, y2 = bbox

            # Convert bounding box to its center point.
            record["center_xy"] = [
                (x1 + x2) / 2,
                (y1 + y2) / 2,
            ]

            records.append(record)

    print(f"Trajectory records loaded: {len(records)}")

    findings = analyze_interactions(records)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        for finding in findings:
            file.write(json.dumps(finding) + "\n")

    print(f"Potential interactions found: {len(findings)}")
    print(f"Results saved to: {OUTPUT_PATH}")

    for finding in findings[:10]:
        print(
            f"Time: {finding['timestamp_seconds']:.3f}s | "
            f"Tracks: {finding['track_ids']} | "
            f"Distance: {finding['distance_px']} px | "
            f"Closing speed: "
            f"{finding['closing_speed_px_per_second']} px/s"
        )

    if not findings:
        print(
            "No interactions met the current heuristic thresholds. "
            "This does not prove that the video contains no hazards."
        )


if __name__ == "__main__":
    main()
