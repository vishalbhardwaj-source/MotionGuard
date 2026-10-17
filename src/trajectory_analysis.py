import math
from collections import defaultdict


def analyze_trajectories(
    records,
    stationary_threshold_px=2.0,
    max_gap_seconds=0.2,
):
    """Calculate image-space motion signals for tracked objects.

    Displacement and speed are measured in pixels and pixels/second.
    They are not calibrated real-world measurements.
    """
    if stationary_threshold_px < 0:
        raise ValueError("Stationary threshold cannot be negative.")
    if not math.isfinite(stationary_threshold_px):
        raise ValueError("Stationary threshold must be finite.")
    if max_gap_seconds <= 0 or not math.isfinite(max_gap_seconds):
        raise ValueError("Maximum gap must be positive and finite.")

    grouped = defaultdict(list)

    for record in records:
        required = {
            "frame_index",
            "timestamp_seconds",
            "track_id",
            "class_name",
            "bbox_xyxy",
        }
        if not isinstance(record, dict) or not required.issubset(record):
            raise ValueError("Trajectory record is missing required fields.")

        frame = record["frame_index"]
        timestamp = record["timestamp_seconds"]
        bbox = record["bbox_xyxy"]

        if isinstance(frame, bool) or not isinstance(frame, int) or frame < 0:
            raise ValueError("Frame index must be a non-negative integer.")

        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (int, float))
            or not math.isfinite(timestamp)
            or timestamp < 0
        ):
            raise ValueError("Timestamp must be finite and non-negative.")

        if (
            not isinstance(bbox, list)
            or len(bbox) != 4
            or any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not math.isfinite(v)
                for v in bbox
            )
        ):
            raise ValueError("Bounding box must contain four finite numbers.")

        x1, y1, x2, y2 = bbox
        if x2 <= x1 or y2 <= y1:
            raise ValueError("Bounding box must have positive area.")

        item = dict(record)
        item["_center_x"] = (x1 + x2) / 2
        item["_center_y"] = (y1 + y2) / 2
        item["_area"] = (x2 - x1) * (y2 - y1)
        grouped[record["track_id"]].append(item)

    results = []

    for track_id, observations in grouped.items():
        observations.sort(
            key=lambda item: (
                item["frame_index"],
                item["timestamp_seconds"],
            )
        )

        previous = None
        stationary_start = None

        for current in observations:
            timestamp = current["timestamp_seconds"]
            center = (current["_center_x"], current["_center_y"])

            displacement = None
            image_speed = None
            area_change_ratio = None
            stationary_duration = 0.0

            if previous is not None:
                previous_time = previous["timestamp_seconds"]
                elapsed = timestamp - previous_time

                if elapsed < 0:
                    raise ValueError("Timestamps must be ordered per track.")

                if elapsed == 0:
                    raise ValueError(
                        "Consecutive observations for a track need "
                        "distinct timestamps."
                    )

                if elapsed <= max_gap_seconds:
                    dx = center[0] - previous["_center_x"]
                    dy = center[1] - previous["_center_y"]
                    displacement = math.hypot(dx, dy)
                    image_speed = displacement / elapsed

                    area_change_ratio = (
                        current["_area"] / previous["_area"]
                    ) - 1.0

                    if displacement <= stationary_threshold_px:
                        if stationary_start is None:
                            stationary_start = previous_time
                        stationary_duration = timestamp - stationary_start
                    else:
                        stationary_start = None
                else:
                    # Do not infer motion across a long missing-observation gap.
                    stationary_start = None

            result = {
                key: value
                for key, value in current.items()
                if not key.startswith("_")
            }
            result.update({
                "center_xy": [
                    round(current["_center_x"], 2),
                    round(current["_center_y"], 2),
                ],
                "bbox_area_px2": round(current["_area"], 2),
                "displacement_px": (
                    round(displacement, 3)
                    if displacement is not None else None
                ),
                "image_speed_px_per_second": (
                    round(image_speed, 3)
                    if image_speed is not None else None
                ),
                "bbox_area_change_ratio": (
                    round(area_change_ratio, 4)
                    if area_change_ratio is not None else None
                ),
                "stationary_duration_seconds": round(
                    stationary_duration, 3
                ),
            })
            results.append(result)
            previous = current

    results.sort(
        key=lambda item: (
            item["frame_index"],
            item["timestamp_seconds"],
            str(item["track_id"]),
        )
    )
    return results
