def aggregate_interaction_events(findings, max_gap_seconds=0.5):
    """Group repeated findings for the same pair into event episodes.

    A new episode starts when the gap between consecutive findings
    exceeds max_gap_seconds. These are review events, not confirmed
    collisions.
    """
    if (
        isinstance(max_gap_seconds, bool)
        or not isinstance(max_gap_seconds, (int, float))
        or max_gap_seconds <= 0
    ):
        raise ValueError("max_gap_seconds must be positive.")

    grouped = {}

    for finding in findings:
        pair = tuple(sorted(finding["track_ids"], key=str))
        grouped.setdefault(pair, []).append(finding)

    events = []

    for pair, items in grouped.items():
        items.sort(key=lambda item: item["timestamp_seconds"])
        episodes = []
        current = []

        for item in items:
            if current and (
                item["timestamp_seconds"]
                - current[-1]["timestamp_seconds"]
                > max_gap_seconds
            ):
                episodes.append(current)
                current = []

            current.append(item)

        if current:
            episodes.append(current)

        for episode in episodes:
            closest = min(
                episode,
                key=lambda item: item["distance_px"],
            )
            fastest = max(
                episode,
                key=lambda item: item["closing_speed_px_per_second"],
            )

            valid_ttcs = [
                item["time_to_collision_seconds"]
                for item in episode
                if item.get("time_to_collision_seconds") is not None
            ]
            min_ttc = min(valid_ttcs) if valid_ttcs else None

            valid_norm_dists = [
                item["normalized_distance"]
                for item in episode
                if item.get("normalized_distance") is not None
            ]
            min_norm_dist = min(valid_norm_dists) if valid_norm_dists else None

            peak_iou = max((item.get("bbox_iou") or 0.0) for item in episode)
            contact_frame_count = sum(1 for item in episode if (item.get("bbox_iou") or 0.0) >= 0.05)
            all_signals = list({
                sig
                for item in episode
                for sig in item.get("post_impact_signals", [])
            })

            events.append({
                "event_id": f"PI-{len(events) + 1:04d}",
                "track_ids": list(pair),
                "start_seconds": episode[0]["timestamp_seconds"],
                "end_seconds": episode[-1]["timestamp_seconds"],
                "duration_seconds": round(
                    episode[-1]["timestamp_seconds"]
                    - episode[0]["timestamp_seconds"],
                    3,
                ),
                "detection_count": len({
                    item["timestamp_seconds"] for item in episode
                }),
                "contact_frame_count": contact_frame_count,
                "peak_confirmation_count": max(
                    item.get("consecutive_confirmation_count", 0)
                    for item in episode
                ),
                "minimum_distance_px": closest["distance_px"],
                "minimum_distance_timestamp_seconds": (
                    closest["timestamp_seconds"]
                ),
                "peak_closing_speed_px_per_second": (
                    fastest["closing_speed_px_per_second"]
                ),
                "peak_closing_speed_timestamp_seconds": (
                    fastest["timestamp_seconds"]
                ),
                "evidence_timestamp_seconds": (
                    closest["timestamp_seconds"]
                ),
                "minimum_ttc_seconds": min_ttc,
                "minimum_normalized_distance": min_norm_dist,
                "peak_bbox_iou": peak_iou,
                "post_impact_signals": all_signals,
                "finding": "POTENTIAL_APPROACHING_INTERACTION",
                "confidence": "UNVALIDATED_HEURISTIC",
                "limitations": [
                    "Image-space measurements are not real-world distances.",
                    "A potential interaction does not establish a collision.",
                ],
            })

    events.sort(key=lambda event: event["start_seconds"])

    # Assign IDs after chronological sorting.
    for index, event in enumerate(events, start=1):
        event["event_id"] = f"PI-{index:04d}"

    return events
