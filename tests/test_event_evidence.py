
import json
from pathlib import Path

import cv2


VIDEO_PATH = Path("data/videos/normal.mp4")
EVENTS_PATH = Path("outputs/interaction_events_test.jsonl")
EVIDENCE_DIR = Path("outputs/event_evidence_test")





def draw_event_evidence(frame, event, trajectory_records):
    timestamp = event["minimum_distance_timestamp_seconds"]
    track_ids = sorted(set(event["track_ids"]))
    height, width = frame.shape[:2]

    # Dark header for a clean, readable evidence image.
    header_height = 62
    cv2.rectangle(
        frame,
        (0, 0),
        (width, header_height),
        (30, 30, 30),
        -1,
    )

    title = f"{event['event_id']} | POTENTIAL INTERACTION"
    details = (
        f"Time: {timestamp:.3f}s | "
        f"Minimum center distance: "
        f"{event['minimum_distance_px']:.2f} px"
    )

    cv2.putText(
        frame, title, (12, 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65,
        (255, 255, 255), 2, cv2.LINE_AA,
    )
    cv2.putText(
        frame, details, (12, 49),
        cv2.FONT_HERSHEY_SIMPLEX, 0.48,
        (220, 220, 220), 1, cv2.LINE_AA,
    )

    # Highlight only the tracks associated with this event.
    colors = [
        (0, 220, 0),       # Green
        (0, 165, 255),     # Orange
    ]

    matched_records = []

    for track_id in track_ids:
        candidates = [
            record for record in trajectory_records
            if record.get("track_id") == track_id
            and abs(
                record.get("timestamp_seconds", -999) - timestamp
            ) <= 0.1
        ]

        if not candidates:
            continue

        record = min(
            candidates,
            key=lambda item: abs(
                item["timestamp_seconds"] - timestamp
            ),
        )

        bbox = record.get("bbox_xyxy")
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            continue

        matched_records.append((track_id, record, bbox))

    for index, (track_id, record, bbox) in enumerate(matched_records):
        x1, y1, x2, y2 = map(int, bbox)

        x1 = max(0, min(width - 1, x1))
        x2 = max(0, min(width - 1, x2))
        y1 = max(0, min(height - 1, y1))
        y2 = max(0, min(height - 1, y2))

        if x2 <= x1 or y2 <= y1:
            continue

        color = colors[index % len(colors)]
        class_name = record.get("class_name", "object")
        label = f"EVENT TRACK {track_id} | {class_name}"

        cv2.rectangle(
            frame, (x1, y1), (x2, y2), color, 3
        )

        label_y = y1 - 9 if y1 > header_height + 25 else y1 + 22

        cv2.putText(
            frame, label, (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.52,
            color, 2, cv2.LINE_AA,
        )

    if len(matched_records) < 2:
        warning = "WARNING: Could not match both event tracks at this timestamp"
        cv2.putText(
            frame, warning, (12, height - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (0, 0, 255), 2, cv2.LINE_AA,
        )

    return frame



def main():
    if not VIDEO_PATH.exists():
        raise FileNotFoundError(f"Video not found: {VIDEO_PATH}")

    if not EVENTS_PATH.exists():
        raise FileNotFoundError(f"Events file not found: {EVENTS_PATH}")

    with EVENTS_PATH.open("r", encoding="utf-8") as file:
        events = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    trajectory_path = Path("outputs/trajectories_trails_test.jsonl")

    if not trajectory_path.exists():
        raise FileNotFoundError(
            f"Trajectory file not found: {trajectory_path}"
        )

    with trajectory_path.open("r", encoding="utf-8") as file:
        trajectory_records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    print("Trajectory records loaded:", len(trajectory_records))

    if not events:
        print("No events to inspect.")
        return

    # Generate evidence for every event.
    selected = events

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(VIDEO_PATH))

    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    saved = 0

    try:
        for event in selected:
            timestamp = event["minimum_distance_timestamp_seconds"]
            frame_number = max(0, round(timestamp * fps))

            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = capture.read()

            if not success:
                print(
                    f"Could not read frame for {event['event_id']} "
                    f"at {timestamp:.3f}s"
                )
                continue
            frame = draw_event_evidence(
                frame, event, trajectory_records
            )
            output_path = EVIDENCE_DIR / f"{event['event_id']}.jpg"

            if not cv2.imwrite(str(output_path), frame):
                print(f"Could not save: {output_path}")
                continue

            saved += 1
            print(
                f"{event['event_id']} | "
                f"Closest-approach time: {timestamp:.3f}s | "
                f"Tracks: {event['track_ids']} | "
                f"Min distance: {event['minimum_distance_px']} px | "
                f"Saved: {output_path}"
            )
    finally:
        capture.release()

    print(f"\nSaved {saved} evidence frames to {EVIDENCE_DIR}")


if __name__ == "__main__":
    main()

