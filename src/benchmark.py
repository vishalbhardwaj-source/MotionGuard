import math
from pathlib import Path


def evaluate_detections_against_ground_truth(
    detected_events,
    ground_truth_crashes,
    video_duration_seconds,
    temporal_tolerance_seconds=1.5,
):
    """
    Evaluate collision and near-miss detections against ground-truth crash intervals
    (e.g., DoTA, CCD, or Nexar benchmark formats).

    Returns:
      - Precision, Recall, F1 Score
      - Mean Detection Delay (seconds)
      - False Alarms per Hour of Video (FA/hr)
    """
    if video_duration_seconds <= 0:
        raise ValueError("Video duration must be greater than zero.")

    matched_gt = set()
    matched_detections = set()
    delays = []

    # Match each detection to ground truth windows
    for det_idx, det in enumerate(detected_events):
        det_time = det.get("evidence_timestamp_seconds")
        if det_time is None:
            det_time = det.get("minimum_distance_timestamp_seconds", det.get("start_seconds", 0.0))

        for gt_idx, gt in enumerate(ground_truth_crashes):
            gt_start = gt.get("start_s", 0.0)
            gt_end = gt.get("end_s", gt_start + 1.0)

            # Match condition: detection occurs within ground truth crash window +/- tolerance
            if (gt_start - temporal_tolerance_seconds) <= det_time <= (gt_end + temporal_tolerance_seconds):
                matched_gt.add(gt_idx)
                matched_detections.add(det_idx)
                # Delay = how soon after crash onset did the system trigger
                delay = max(0.0, det_time - gt_start)
                delays.append(delay)
                break

    tp = len(matched_gt)
    fp = len(detected_events) - len(matched_detections)
    fn = len(ground_truth_crashes) - len(matched_gt)

    precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if len(ground_truth_crashes) == 0 and fp == 0 else 0.0)
    recall = tp / (tp + fn) if (tp + fn) > 0 else (1.0 if len(ground_truth_crashes) == 0 else 0.0)
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    duration_hours = video_duration_seconds / 3600.0
    false_alarms_per_hour = fp / duration_hours if duration_hours > 0 else 0.0
    mean_delay = sum(delays) / len(delays) if delays else 0.0

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "mean_detection_delay_seconds": round(mean_delay, 2),
        "false_alarms_per_hour": round(false_alarms_per_hour, 2),
        "video_duration_seconds": round(video_duration_seconds, 2),
        "total_ground_truth_accidents": len(ground_truth_crashes),
        "total_detected_events": len(detected_events),
    }


def format_benchmark_table(evaluation_results):
    """Format benchmark evaluation metrics into clean GitHub-ready Markdown."""
    res = evaluation_results
    return f"""### 📊 Empirical Ground-Truth Benchmark Results

| Metric | Measured Value | Standard Target | Interpretation |
| :--- | :---: | :---: | :--- |
| **Precision** | **{res['precision'] * 100:.1f}%** | > 80% | Ratio of true alerts to total candidate alerts |
| **Recall** | **{res['recall'] * 100:.1f}%** | > 85% | Ratio of detected accidents to actual accidents |
| **F1 Score** | **{res['f1_score']:.3f}** | > 0.82 | Harmonic mean of precision and recall |
| **Detection Delay** | **{res['mean_detection_delay_seconds']:.2f}s** | < 1.0s | Average latency from crash onset to trigger |
| **False Alarms / Hour** | **{res['false_alarms_per_hour']:.1f} FA/hr** | Low | Expected nuisance alerts per stream-hour |
"""
