import math
from collections import defaultdict
from src.zones import find_zone_for_point, get_contextual_threshold_multiplier


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


def calculate_normalized_distance(distance_px, box_a, box_b):
    """
    Calculate Euclidean separation normalized by vehicle bounding box scale.
    Normalized distance < 1.0 means vehicles are closer than their own average size.
    """
    if not box_a or not box_b or len(box_a) != 4 or len(box_b) != 4:
        return None

    w_a = abs(box_a[2] - box_a[0])
    h_a = abs(box_a[3] - box_a[1])
    w_b = abs(box_b[2] - box_b[0])
    h_b = abs(box_b[3] - box_b[1])

    scale_a = max(w_a, h_a)
    scale_b = max(w_b, h_b)
    avg_scale = (scale_a + scale_b) / 2.0

    if avg_scale <= 0:
        return None
    return distance_px / avg_scale


def calculate_ttc(distance_px, closing_speed_px_s):
    """
    Compute Time-To-Collision (TTC) in seconds.
    TTC = distance / closing_speed for closing trajectories.
    """
    if closing_speed_px_s is None or closing_speed_px_s <= 0.001:
        return float("inf")
    return distance_px / closing_speed_px_s


def calculate_monocular_scale_ttc(box_current, box_previous, dt):
    """
    Calculate optical scale-growth Time-To-Collision (Lee's Tau: tau = s / (ds/dt)).
    Estimates time to impact purely from bounding box expansion rate,
    making it robust to monocular perspective foreshortening.
    """
    if (
        not box_current
        or not box_previous
        or len(box_current) != 4
        or len(box_previous) != 4
        or dt <= 0.001
    ):
        return float("inf")

    s_curr = math.sqrt(abs(box_current[2] - box_current[0]) * abs(box_current[3] - box_current[1]))
    s_prev = math.sqrt(abs(box_previous[2] - box_previous[0]) * abs(box_previous[3] - box_previous[1]))

    growth_rate = (s_curr - s_prev) / dt
    if growth_rate <= 0.05:
        return float("inf")

    tau = s_curr / growth_rate
    return max(0.0, tau)


def detect_post_impact_kinematics(observations, contact_time, window_seconds=0.6, drop_ratio=0.40):
    """
    Detect post-impact kinematic anomalies: sudden deceleration or vehicle stopping
    within window_seconds after point of closest approach/contact.
    """
    pre_speeds = []
    post_speeds = []

    for obs in observations:
        t = obs["timestamp"]
        vel = obs.get("velocity")
        if vel is None:
            continue
        speed = math.hypot(vel[0], vel[1])
        if contact_time - window_seconds <= t < contact_time:
            pre_speeds.append(speed)
        elif contact_time <= t <= contact_time + window_seconds:
            post_speeds.append(speed)

    if not pre_speeds or not post_speeds:
        return None

    avg_pre = sum(pre_speeds) / len(pre_speeds)
    avg_post = sum(post_speeds) / len(post_speeds)

    signals = []
    if avg_pre > 10.0 and (avg_pre - avg_post) / avg_pre >= drop_ratio:
        signals.append("SUDDEN_DECELERATION")
    if avg_post < 3.0 and avg_pre > 15.0:
        signals.append("VEHICLE_STOPPED_AFTER_CONTACT")

    return signals if signals else None


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
    max_ttc_seconds=None,
    max_normalized_distance=None,
    zones=None,
    min_iou_contact=None,
    deceleration_post_impact_threshold=None,
):
    """
    Flag candidate interactions between tracked vehicles using scale-normalized
    distance, closing speed, Time-To-Collision (TTC), and box overlap.

    Measurements use image-space pixels and surrogate safety metrics.
    Results are candidates for operator triage, not certified collision claims.
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

    if min_iou_contact is None or deceleration_post_impact_threshold is None:
        try:
            from src.config import load_config
            k_cfg = load_config().get("kinematics", {})
            if min_iou_contact is None:
                min_iou_contact = k_cfg.get("min_iou_contact", 0.05)
            if deceleration_post_impact_threshold is None:
                deceleration_post_impact_threshold = k_cfg.get("deceleration_post_impact_threshold", 0.50)
        except Exception:
            min_iou_contact = min_iou_contact if min_iou_contact is not None else 0.05
            deceleration_post_impact_threshold = deceleration_post_impact_threshold if deceleration_post_impact_threshold is not None else 0.50

    if (
        isinstance(min_consecutive_matches, bool)
        or not isinstance(min_consecutive_matches, int)
        or min_consecutive_matches < 1
    ):
        raise ValueError("min_consecutive_matches must be a positive integer.")

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

    # Build valid per-track movement observations
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

    # Compare observations only when timestamps match
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

                # Missing velocity breaks the confirmation sequence
                if first["velocity"] is None or second["velocity"] is None:
                    consecutive_matches = 0
                    previous_timestamp = None
                    continue

                dx = second["center"][0] - first["center"][0]
                dy = second["center"][1] - first["center"][1]
                distance = math.hypot(dx, dy)

                # Contextual Zone modulation
                zone_1 = find_zone_for_point(first["center"], zones) if zones else None
                zone_2 = find_zone_for_point(second["center"], zones) if zones else None
                zone_mult, zone_ctx = get_contextual_threshold_multiplier(zone_1, zone_2) if zones else (1.0, "UNZONED")
                effective_proximity_px = proximity_threshold_px * zone_mult

                if distance == 0 or distance > effective_proximity_px:
                    consecutive_matches = 0
                    previous_timestamp = None
                    continue

                relative_vx = second["velocity"][0] - first["velocity"][0]
                relative_vy = second["velocity"][1] - first["velocity"][1]

                # Positive means the distance between objects is shrinking
                closing_speed = -(
                    dx * relative_vx + dy * relative_vy
                ) / distance

                if closing_speed < min_closing_speed_px_s:
                    consecutive_matches = 0
                    previous_timestamp = None
                    continue

                # Compute Time-To-Collision (TTC)
                ttc = calculate_ttc(distance, closing_speed)
                if max_ttc_seconds is not None and ttc > max_ttc_seconds:
                    consecutive_matches = 0
                    previous_timestamp = None
                    continue

                # Compute scale-normalized distance and IoU if boxes exist
                box_a = first.get("bbox_xyxy")
                box_b = second.get("bbox_xyxy")
                norm_dist = calculate_normalized_distance(distance, box_a, box_b)
                current_iou = bbox_iou(box_a, box_b) or 0.0

                if max_normalized_distance is not None and norm_dist is not None:
                    if norm_dist > max_normalized_distance and current_iou <= 0.0:
                        consecutive_matches = 0
                        previous_timestamp = None
                        continue

                # Confirmation requires consecutive qualifying timestamps
                prior_timestamp = previous_timestamp
                if (
                    prior_timestamp is not None
                    and timestamp - prior_timestamp <= max_gap_seconds
                ):
                    consecutive_matches += 1
                else:
                    consecutive_matches = 1

                previous_timestamp = timestamp

                if consecutive_matches < min_consecutive_matches:
                    continue

                # Post-impact kinematic signal detection using configured deceleration threshold
                signals_1 = detect_post_impact_kinematics(
                    observations[first_id], timestamp, drop_ratio=deceleration_post_impact_threshold
                ) or []
                signals_2 = detect_post_impact_kinematics(
                    observations[second_id], timestamp, drop_ratio=deceleration_post_impact_threshold
                ) or []
                combined_signals = list(set(signals_1 + signals_2))

                # Optical Tau TTC calculation if consecutive boxes exist (using prior_timestamp)
                tau_a = float("inf")
                tau_b = float("inf")
                if prior_timestamp is not None:
                    prev_first = first_by_time.get(prior_timestamp)
                    prev_second = second_by_time.get(prior_timestamp)
                    p_dt = timestamp - prior_timestamp
                    if prev_first and p_dt > 0:
                        tau_a = calculate_monocular_scale_ttc(box_a, prev_first.get("bbox_xyxy"), p_dt)
                    if prev_second and p_dt > 0:
                        tau_b = calculate_monocular_scale_ttc(box_b, prev_second.get("bbox_xyxy"), p_dt)
                min_tau = min(tau_a, tau_b)

                finding_entry = {
                    "timestamp_seconds": timestamp,
                    "frame_index": first["frame_index"],
                    "track_ids": [first_id, second_id],
                    "consecutive_confirmation_count": consecutive_matches,
                    "distance_px": round(distance, 2),
                    "closing_speed_px_per_second": round(closing_speed, 2),
                    "time_to_collision_seconds": round(ttc, 2) if math.isfinite(ttc) else None,
                    "optical_tau_ttc_seconds": round(min_tau, 2) if math.isfinite(min_tau) else None,
                    "normalized_distance": round(norm_dist, 2) if norm_dist is not None else None,
                    "bbox_iou": round(current_iou, 3),
                    "post_impact_signals": combined_signals,
                    "zone_context": zone_ctx if zones else None,
                    "zone_multiplier": zone_mult if zones else 1.0,
                    "zone_name_primary": zone_1.name if zone_1 else None,
                    "finding": "POTENTIAL_APPROACHING_INTERACTION",
                    "confidence": "UNVALIDATED_HEURISTIC",
                    "limitations": [
                        "Image-space distance is not real-world metric distance.",
                        "A potential interaction indicates proximity dynamics for review.",
                    ],
                }
                findings.append(finding_entry)

    return findings
