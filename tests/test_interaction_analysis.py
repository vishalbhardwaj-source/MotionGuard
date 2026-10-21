
from src.interaction_analysis import analyze_interactions, bbox_iou
from src.interaction_analysis import is_persistent_duplicate


def make_records(first_positions, second_positions, times=(0.0, 0.1)):
    records = []

    for track_id, positions in (
        (1, first_positions),
        (2, second_positions),
    ):
        for frame_index, (timestamp, x) in enumerate(
            zip(times, positions)
        ):
            records.append({
                "frame_index": frame_index,
                "timestamp_seconds": timestamp,
                "track_id": track_id,
                "center_xy": [x, 100.0],
            })

    return records



def test_approaching_objects():
    records = make_records(
        [0, 10, 20, 30],
        [100, 90, 80, 70],
        times=(0.0, 0.1, 0.2, 0.3),
    )

    findings = analyze_interactions(
        records,
        proximity_threshold_px=80,
        min_closing_speed_px_s=5,
    )

    assert len(findings) == 1, findings
    assert findings[0]["finding"] == (
        "POTENTIAL_APPROACHING_INTERACTION"
    )
    assert findings[0]["distance_px"] == 40.0
    assert findings[0]["closing_speed_px_per_second"] == 200.0
    assert findings[0]["timestamp_seconds"] == 0.3
    print("PASS: approaching objects require persistent confirmation")



def test_separating_objects():
    records = make_records([10, 0], [90, 100])

    findings = analyze_interactions(
        records,
        proximity_threshold_px=120,
        min_closing_speed_px_s=5,
    )

    assert findings == [], findings
    print("PASS: separating objects are not flagged")


def test_objects_too_far_apart():
    records = make_records([0, 10], [200, 190])

    findings = analyze_interactions(
        records,
        proximity_threshold_px=80,
        min_closing_speed_px_s=5,
    )

    assert findings == [], findings
    print("PASS: distant objects are not flagged")


def test_stationary_objects():
    records = make_records([10, 10], [60, 60])

    findings = analyze_interactions(
        records,
        proximity_threshold_px=80,
        min_closing_speed_px_s=5,
    )

    assert findings == [], findings
    print("PASS: stationary objects are not flagged")



def test_excluded_train_pair():
    records = make_records([0, 10], [100, 90])

    for record in records:
        record["class_name"] = (
            "car" if record["track_id"] == 1 else "train"
        )

    findings = analyze_interactions(
        records,
        proximity_threshold_px=80,
        min_closing_speed_px_s=5,
        excluded_classes=("train",),
    )

    assert findings == [], findings
    print("PASS: car-train pairs are excluded")

def test_insufficient_observations():
    records = [
        {
            "frame_index": 0,
            "timestamp_seconds": 0.0,
            "track_id": 1,
            "center_xy": [10.0, 100.0],
        },
        {
            "frame_index": 0,
            "timestamp_seconds": 0.0,
            "track_id": 2,
            "center_xy": [60.0, 100.0],
        },
    ]

    findings = analyze_interactions(records)
    assert findings == [], findings
    print("PASS: insufficient observations produce no finding")



def test_duplicate_bounding_boxes_are_filtered():
    records = make_records(
        [0, 10, 20],
        [100, 90, 80],
        times=(0.0, 0.1, 0.2),
    )
    for record in records:
        record["bbox_xyxy"] = (
            [10, 10, 110, 110]
            if record["track_id"] == 1
            else [10.1, 10.1, 110.1, 110.1]
        )

    assert bbox_iou(
        [10, 10, 110, 110],
        [10.1, 10.1, 110.1, 110.1],
    ) >= 0.95

    findings = analyze_interactions(
        records,
        proximity_threshold_px=80,
        min_closing_speed_px_s=5,
    )

    assert findings == [], findings
    print("PASS: near-identical bounding boxes are filtered")

if __name__ == "__main__":
    test_approaching_objects()
    test_excluded_train_pair()
    test_separating_objects()
    test_objects_too_far_apart()
    test_stationary_objects()
    test_insufficient_observations()
    test_duplicate_bounding_boxes_are_filtered()

    print("\nAll interaction-analysis tests passed!")

def test_same_class_duplicate_tracks_with_partial_overlap():
    first_observations = [
        {
            "timestamp": timestamp,
            "bbox_xyxy": [x, 100, x + 40, 140],
        }
        for timestamp, x in (
            (0.0, 100),
            (0.1, 102),
            (0.2, 101),
        )
    ]

    second_observations = [
        {
            "timestamp": timestamp,
            "bbox_xyxy": [x, 100, x + 40, 140],
        }
        for timestamp, x in (
            (0.0, 112),
            (0.1, 114),
            (0.2, 113),
        )
    ]

    result = is_persistent_duplicate(
        first_observations,
        second_observations,
        {"car"},
        {"car"},
        min_iou=0.50,
        min_matches=3,
        max_gap_seconds=0.2,
    )

    assert result is True, (
        "Persistent same-class tracks with partial overlap "
        "should be identified by the duplicate detector."
    )


def test_same_class_tracks_with_03853_iou():
    first_observations = [
        {
            "timestamp": timestamp,
            "bbox_xyxy": [1214.51, 41.86, 1235.08, 97.07],
        }
        for timestamp in (6.54, 6.573, 6.607)
    ]

    second_observations = [
        {
            "timestamp": timestamp,
            "bbox_xyxy": [1221.77, 39.66, 1247.96, 97.18],
        }
        for timestamp in (6.54, 6.573, 6.607)
    ]

    overlap = bbox_iou(
        first_observations[-1]["bbox_xyxy"],
        second_observations[-1]["bbox_xyxy"],
    )

    print(f"Actual-case IoU: {overlap:.4f}")

    result = is_persistent_duplicate(
        first_observations,
        second_observations,
        {"person"},
        {"person"},
        min_iou=0.50,
        min_matches=3,
        max_gap_seconds=0.2,
    )

    print(f"Duplicate filter result: {result}")



def test_ttc_calculation_and_filtering():
    from src.interaction_analysis import calculate_ttc

    # 100px at 50px/s closing speed = 2.0s TTC
    assert calculate_ttc(100.0, 50.0) == 2.0
    # Negative or 0 closing speed = inf
    assert calculate_ttc(100.0, 0.0) == float("inf")
    assert calculate_ttc(100.0, -10.0) == float("inf")

    # Approaching objects with distance 40px and closing speed 10px/s -> TTC = 4.0s
    records = make_records(
        [0, 1, 2, 3],
        [43, 42, 41, 40],
        times=(0.0, 0.1, 0.2, 0.3),
    )
    # When max_ttc_seconds=2.0, TTC is ~3.7s so it should be filtered out
    findings = analyze_interactions(
        records,
        proximity_threshold_px=80,
        min_closing_speed_px_s=5,
        max_ttc_seconds=2.0,
    )
    assert findings == []


def test_normalized_distance_calculation():
    from src.interaction_analysis import calculate_normalized_distance

    box_a = [0, 0, 50, 50]   # scale = 50
    box_b = [70, 0, 120, 50] # scale = 50
    # Center-to-center distance is 70px. avg_scale = 50 -> norm_dist = 1.4
    norm_dist = calculate_normalized_distance(70.0, box_a, box_b)
    assert round(norm_dist, 2) == 1.40


def test_post_impact_kinematics_detection():
    from src.interaction_analysis import detect_post_impact_kinematics

    # Vehicle cruising fast, then abruptly halts at contact time 1.0s
    obs = [
        {"timestamp": 0.5, "velocity": (30.0, 0.0)},
        {"timestamp": 0.8, "velocity": (28.0, 0.0)},
        {"timestamp": 1.0, "velocity": (2.0, 0.0)},
        {"timestamp": 1.2, "velocity": (0.0, 0.0)},
    ]
    signals = detect_post_impact_kinematics(obs, contact_time=1.0)
    assert signals is not None
    assert "SUDDEN_DECELERATION" in signals or "VEHICLE_STOPPED_AFTER_CONTACT" in signals


def test_monocular_scale_ttc():
    from src.interaction_analysis import calculate_monocular_scale_ttc

    # Box growing from 50x50 to 60x60 in 0.1s
    # scale_prev = 50, scale_curr = 60, growth = 100/s -> tau = 60 / 100 = 0.60s
    box_prev = [0, 0, 50, 50]
    box_curr = [0, 0, 60, 60]
    tau = calculate_monocular_scale_ttc(box_curr, box_prev, dt=0.1)
    assert round(tau, 2) == 0.60

    # Shrinking or stagnant box returns inf
    box_shrink = [0, 0, 45, 45]
    assert calculate_monocular_scale_ttc(box_shrink, box_curr, dt=0.1) == float("inf")


def test_optical_tau_ttc_computes_finite_value():
    # Track 1 stationary, Track 2 approaching and looming (growing bbox)
    records = []
    for f in range(4):
        t = f * 0.1
        w = 20.0 + f * 5.0
        records.append({
            "frame_index": f,
            "timestamp_seconds": t,
            "track_id": 1,
            "center_xy": (50.0, 50.0),
            "bbox_xyxy": [40, 40, 60, 60],
        })
        records.append({
            "frame_index": f,
            "timestamp_seconds": t,
            "track_id": 2,
            "center_xy": (100.0 - f * 8.0, 50.0),
            "bbox_xyxy": [100.0 - f * 8.0 - w / 2, 50 - w / 2, 100.0 - f * 8.0 + w / 2, 50 + w / 2],
        })

    findings = analyze_interactions(
        records,
        proximity_threshold_px=80.0,
        min_closing_speed_px_s=1.0,
        min_consecutive_matches=2,
    )
    assert len(findings) > 0
    valid_taus = [
        f["optical_tau_ttc_seconds"]
        for f in findings
        if f.get("optical_tau_ttc_seconds") is not None
    ]
    assert len(valid_taus) > 0
    assert all(tau > 0 for tau in valid_taus)
