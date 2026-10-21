import pytest
from src.benchmark import evaluate_detections_against_ground_truth, format_benchmark_table


def test_benchmark_perfect_detection():
    detected = [
        {"evidence_timestamp_seconds": 5.2, "event_id": "EVT-01"},
    ]
    gt = [
        {"start_s": 5.0, "end_s": 6.0, "label": "collision"},
    ]
    # 60s video
    eval_res = evaluate_detections_against_ground_truth(detected, gt, video_duration_seconds=60.0)
    assert eval_res["true_positives"] == 1
    assert eval_res["false_positives"] == 0
    assert eval_res["false_negatives"] == 0
    assert eval_res["precision"] == 1.0
    assert eval_res["recall"] == 1.0
    assert eval_res["f1_score"] == 1.0
    assert eval_res["mean_detection_delay_seconds"] == 0.2
    assert eval_res["false_alarms_per_hour"] == 0.0

    table_md = format_benchmark_table(eval_res)
    assert "100.0%" in table_md


def test_benchmark_normal_safe_traffic_no_crashes():
    # Normal safe traffic clip: 0 true crashes, 1 false alarm over 120s
    detected = [
        {"evidence_timestamp_seconds": 15.0, "event_id": "EVT-FALSE-01"},
    ]
    gt = []
    eval_res = evaluate_detections_against_ground_truth(detected, gt, video_duration_seconds=120.0)
    assert eval_res["true_positives"] == 0
    assert eval_res["false_positives"] == 1
    # 1 alert in 120s (2 minutes) = 30 FA/hr
    assert eval_res["false_alarms_per_hour"] == 30.0


def test_run_standard_benchmark_suite():
    from src.benchmark import run_standard_benchmark_suite, format_dual_benchmark_markdown

    results = run_standard_benchmark_suite()
    assert "safe_traffic" in results
    assert "collision_traffic" in results

    safe = results["safe_traffic"]
    assert safe["false_alarms_per_hour"] == 0.0

    crash = results["collision_traffic"]
    assert crash["precision"] == 1.0
    assert crash["recall"] == 1.0
    assert crash["mean_detection_delay_seconds"] == 0.30

    md = format_dual_benchmark_markdown(results)
    assert "Real Collision Clip" in md
    assert "0.30 seconds" in md
