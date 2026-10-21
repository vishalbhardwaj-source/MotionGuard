import pytest
from src.benchmark import compute_confusion_matrix, filter_events_by_tuning


def test_compute_confusion_matrix_perfect():
    detected = [{"evidence_timestamp_seconds": 5.2, "event_id": "CRASH-01"}]
    gt = [{"start_s": 5.0, "end_s": 6.0, "label": "collision"}]

    cm = compute_confusion_matrix(
        detected_events=detected,
        ground_truth_crashes=gt,
        video_duration_seconds=10.0,
        total_negative_units=299,
    )

    assert cm["TP"] == 1
    assert cm["FP"] == 0
    assert cm["FN"] == 0
    assert cm["TN"] == 299
    assert cm["accuracy"] == 1.0
    assert cm["sensitivity"] == 1.0
    assert cm["precision"] == 1.0
    assert cm["f1_score"] == 1.0
    assert cm["matrix"] == [[1, 0], [0, 299]]


def test_compute_confusion_matrix_false_positive():
    detected = [
        {"evidence_timestamp_seconds": 12.0, "event_id": "FALSE-01"},
    ]
    gt = []

    cm = compute_confusion_matrix(
        detected_events=detected,
        ground_truth_crashes=gt,
        video_duration_seconds=60.0,
        total_negative_units=1800,
    )

    assert cm["TP"] == 0
    assert cm["FP"] == 1
    assert cm["FN"] == 0
    assert cm["TN"] == 1799
    assert cm["precision"] == 0.0
    assert cm["specificity"] < 1.0


def test_filter_events_by_tuning():
    events = [
        {
            "event_id": "EVT-CRASH",
            "peak_bbox_iou": 0.15,
            "minimum_ttc_seconds": 0.8,
            "minimum_normalized_distance": 0.4,
            "peak_closing_speed_px_per_second": 35.0,
        },
        {
            "event_id": "EVT-MERGE",
            "peak_bbox_iou": 0.01,
            "minimum_ttc_seconds": 2.8,
            "minimum_normalized_distance": 1.4,
            "peak_closing_speed_px_per_second": 12.0,
        },
        {
            "event_id": "EVT-BENIGN",
            "peak_bbox_iou": 0.0,
            "minimum_ttc_seconds": 6.5,
            "minimum_normalized_distance": 3.8,
            "peak_closing_speed_px_per_second": 2.0,
        },
    ]

    # Strictest threshold: contact only (IoU >= 0.05)
    contact_only = filter_events_by_tuning(events, iou_thresh=0.05, require_contact=True)
    assert len(contact_only) == 1
    assert contact_only[0]["event_id"] == "EVT-CRASH"

    # Default candidate filtering (TTC <= 3.5s or norm_dist <= 1.8)
    candidates = filter_events_by_tuning(events, max_ttc=3.5, max_norm_dist=1.8, min_closing_speed=5.0)
    assert len(candidates) == 2
    assert {e["event_id"] for e in candidates} == {"EVT-CRASH", "EVT-MERGE"}
