
import math
from collections import defaultdict



def bbox_iou(box_a, box_b):
    """Calculate intersection-over-union for two xyxy bounding boxes."""
    if (
        not isinstance(box_a, (list, tuple))
        or not isinstance(box_b, (list, tuple))
        or len(box_a) != 4
        or len(box_b) != 4
    ):
        return None

    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    if ax2 <= ax1 or ay2 <= ay1 or bx2 <= bx1 or by2 <= by1:
        return None

    intersection_width = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    intersection_height = max(0.0, min(ay2, by2) - max(ay1, by1))
    intersection = intersection_width * intersection_height

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - intersection

    if union <= 0:
        return None

    return intersection / union



def is_persistent_duplicate(
    first_observations,
    second_observations,
    first_classes,
    second_classes,
    min_iou=0.90,
    min_matches=3,
    max_gap_seconds=0.2,
):
    """Flag persistent overlapping tracks that may be duplicate IDs."""
    if first_classes and second_classes and first_classes.isdisjoint(second_classes):
        return False

    # Use a lower overlap threshold for tracks sharing a known class.
    if first_classes and second_classes and not first_classes.isdisjoint(second_classes):
        min_iou = min(min_iou, 0.50)

    first_by_time = {
        item["timestamp"]: item
        for item in first_observations
    }
    second_by_time = {
        item["timestamp"]: item
        for item in second_observations
    }

    matches = sorted(first_by_time.keys() & second_by_time.keys())

    consecutive_matches = 0
    previous_timestamp = None

    for timestamp in matches:
        first = first_by_time[timestamp]
        second = second_by_time[timestamp]

        overlap = bbox_iou(
            first.get("bbox_xyxy"),
            second.get("bbox_xyxy"),
        )

        if overlap is not None and overlap >= min_iou:
            if (
                previous_timestamp is not None
                and timestamp - previous_timestamp <= max_gap_seconds
            ):
                consecutive_matches += 1
            else:
                consecutive_matches = 1

            previous_timestamp = timestamp

            if consecutive_matches >= min_matches:
                return True
        else:
            consecutive_matches = 0
            previous_timestamp = None

    return False



def analyze_interactions(
    records,
    proximity_threshold_px=80.0,
    min_closing_speed_px_s=5.0,
    max_gap_seconds=0.2,
    excluded_classes=("train",),
    min_consecutive_matches=3,
):
    """Flag candidate interactions between tracked objects.

    Measurements use image-space pixels, not calibrated real-world
    distances or speeds. Results are candidates for review, not
    confirmed collision predictions.
    """
    for name, value in (
        ("proximity_threshold_px", proximity_threshold_px),
        ("min_closing_speed_px_s", min_closing_speed_px_s),
        ("max_gap_seconds", max_gap_seconds),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(f"{name} must be finite and non-negative.")

    if max_gap_seconds == 0:
        raise ValueError("max_gap_seconds must be positive.")

    if (
        isinstance(min_consecutive_matches, bool)
        or not isinstance(min_consecutive_matches, int)
        or min_consecutive_matches < 1
    ):
        raise ValueError(
            "min_consecutive_matches must be a positive integer."
        )

    grouped = defaultdict(list)

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each trajectory record must be a dictionary.")

        if "center_xy" not in record and "bbox_xyxy" in record:
            bbox = record["bbox_xyxy"]
            if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                record = dict(record)
                record["center_xy"] = [
                    (bbox[0] + bbox[2]) / 2.0,
                    (bbox[1] + bbox[3]) / 2.0,
                ]

        required = {
            "frame_index",
            "timestamp_seconds",
            "track_id",
            "center_xy",
        }
        if not required.issubset(record):
            raise ValueError("Trajectory record is missing required fields.")

        timestamp = record["timestamp_seconds"]
        center = record["center_xy"]

        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (int, float))
            or not math.isfinite(timestamp)
            or timestamp < 0
        ):
            raise ValueError("Timestamp must be finite and non-negative.")

        if (
            not isinstance(center, (list, tuple))
            or len(center) != 2
            or any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not math.isfinite(v)
                for v in center
            )
        ):
            raise ValueError("center_xy must contain two finite numbers.")

        grouped[record["track_id"]].append({
            **record,
            "center_xy": (float(center[0]), float(center[1])),
        })


    # Build valid per-track movement observations.
    observations = {}
    track_classes = {}

    for track_id, items in grouped.items():
        items.sort(key=lambda item: item["timestamp_seconds"])

        track_classes[track_id] = {
            item.get("class_name")
            for item in items
            if isinstance(item.get("class_name"), str)
        }

        movement = []

        for index, item in enumerate(items):

            velocity = None

            if index > 0:
                previous = items[index - 1]
                dt = item["timestamp_seconds"] - previous["timestamp_seconds"]

                if dt <= 0:
                    raise ValueError(
                        "Timestamps must be distinct and increasing per track."
                    )

                if dt <= max_gap_seconds:
                    velocity = (
                        (item["center_xy"][0] - previous["center_xy"][0]) / dt,
                        (item["center_xy"][1] - previous["center_xy"][1]) / dt,
                    )


            movement.append({
                "timestamp": item["timestamp_seconds"],
                "frame_index": item["frame_index"],
                "center": item["center_xy"],
                "bbox_xyxy": item.get("bbox_xyxy"),
                "velocity": velocity,
            })


        observations[track_id] = movement

    findings = []
    track_ids = list(observations)



    # Compare observations only when timestamps match.
    for i, first_id in enumerate(track_ids):
        for second_id in track_ids[i + 1:]:
            if (
                track_classes[first_id] & set(excluded_classes)
                or track_classes[second_id] & set(excluded_classes)
            ):
                continue

            if is_persistent_duplicate(
                observations[first_id],
                observations[second_id],
                track_classes[first_id],
                track_classes[second_id],
                min_iou=0.90,
                min_matches=3,
                max_gap_seconds=max_gap_seconds,
            ):
                continue

            first_by_time = {
                item["timestamp"]: item
                for item in observations[first_id]
            }
            second_by_time = {
                item["timestamp"]: item
                for item in observations[second_id]
            }


            consecutive_matches = 0
            previous_timestamp = None

            for timestamp in sorted(
                first_by_time.keys() & second_by_time.keys()
            ):
                first = first_by_time[timestamp]
                second = second_by_time[timestamp]

                # Missing velocity breaks the confirmation sequence.
                if first["velocity"] is None or second["velocity"] is None:
                    consecutive_matches = 0
                    previous_timestamp = None
                    continue

                dx = second["center"][0] - first["center"][0]
                dy = second["center"][1] - first["center"][1]
                distance = math.hypot(dx, dy)

                if distance == 0 or distance > proximity_threshold_px:
                    consecutive_matches = 0
                    previous_timestamp = None
                    continue

                relative_vx = second["velocity"][0] - first["velocity"][0]
                relative_vy = second["velocity"][1] - first["velocity"][1]

                # Positive means the distance between objects is shrinking.
                closing_speed = -(
                    dx * relative_vx + dy * relative_vy
                ) / distance

                if closing_speed < min_closing_speed_px_s:
                    consecutive_matches = 0
                    previous_timestamp = None
                    continue

                # Confirmation requires consecutive qualifying timestamps.
                if (
                    previous_timestamp is not None
                    and timestamp - previous_timestamp <= max_gap_seconds
                ):
                    consecutive_matches += 1
                else:
                    consecutive_matches = 1

                previous_timestamp = timestamp

                if consecutive_matches < min_consecutive_matches:
                    continue

                findings.append({
                    "timestamp_seconds": timestamp,
                    "frame_index": first["frame_index"],
                    "track_ids": [first_id, second_id],
                    "consecutive_confirmation_count": consecutive_matches,
                    "distance_px": round(distance, 2),
                    "closing_speed_px_per_second": round(closing_speed, 2),
                    "finding": "POTENTIAL_APPROACHING_INTERACTION",
                    "confidence": "UNVALIDATED_HEURISTIC",
                    "limitations": [
                        "Image-space distance is not real-world distance.",
                        "A potential interaction does not establish a collision.",
                    ],
                })


    return findings

