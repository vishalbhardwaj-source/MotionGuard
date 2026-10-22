import json
import math
import argparse
from pathlib import Path

BENCHMARK_GT_FILE = Path(__file__).resolve().parent.parent / "data" / "benchmarks" / "ground_truth.json"


def load_ground_truth(file_path=None):
    """Load temporal ground-truth crash interval annotations."""
    path = Path(file_path) if file_path else BENCHMARK_GT_FILE
    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


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


def load_or_generate_trajectories(video_path, trajectory_path=None, force_live=False):
    """Load cached trajectory records or run live YOLO tracking if requested/absent."""
    traj_path = Path(trajectory_path) if trajectory_path else None
    if not force_live and traj_path and traj_path.is_file():
        records = []
        with open(traj_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass
        if records:
            return records

    # Run live tracking on the video
    from src.video_processor import track_video
    vid = Path(video_path)
    if not vid.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    out_annotated = Path("outputs") / f"benchmark_tracked_{vid.stem}.mp4"
    out_traj = Path("outputs") / f"benchmark_traj_{vid.stem}.jsonl"
    out_traj.parent.mkdir(parents=True, exist_ok=True)

    track_video(
        str(vid),
        str(out_annotated),
        trajectory_output_path=str(out_traj),
        classes=(2, 3, 5, 7),
    )

    records = []
    with open(out_traj, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def extract_clip_detections(records):
    """
    Run the MotionGuard pipeline (kinematic interaction analysis + event aggregation)
    on multi-vehicle trajectory records using the canonical emergency dispatch rule.
    Returns:
      - candidate_events: all aggregated candidate interactions (analyst triage queue)
      - emergency_dispatches: critical events satisfying automated responder gateway criteria
    """
    from src.interaction_analysis import analyze_interactions
    from src.event_aggregation import aggregate_interaction_events
    from src.risk_engine import is_emergency_dispatch_eligible

    if not records:
        return [], []

    interactions = analyze_interactions(
        records,
        proximity_threshold_px=80.0,
        min_closing_speed_px_s=5.0,
        max_ttc_seconds=3.5,
        max_normalized_distance=1.8,
    )
    events = aggregate_interaction_events(interactions)

    # Use the single canonical qualification rule defined in src/risk_engine.py
    emergency_dispatches = [ev for ev in events if is_emergency_dispatch_eligible(ev)]

    return events, emergency_dispatches


def run_standard_benchmark_suite(ground_truth_file=None, force_live_tracking=False):
    """
    Execute standard evaluation against ground-truth dataset annotations.
    Reads ground-truth intervals from data/benchmarks/ground_truth.json and
    evaluates detection events dynamically from the video clips.
    """
    gt_all = load_ground_truth(ground_truth_file)

    # 1. Normal traffic baseline
    normal_gt_info = gt_all.get("normal.mp4", {})
    normal_duration = float(normal_gt_info.get("duration_seconds", 23.89))
    normal_frames = int(normal_gt_info.get("frame_count", 716))
    normal_crashes = normal_gt_info.get("crashes", [])
    normal_vid_path = normal_gt_info.get("video_path", "data/videos/normal.mp4")
    normal_traj_path = normal_gt_info.get("trajectory_path", "data/benchmarks/normal_trajectories.jsonl")

    normal_recs = load_or_generate_trajectories(
        normal_vid_path, normal_traj_path, force_live=force_live_tracking
    )
    normal_candidates, normal_dispatches = extract_clip_detections(normal_recs)

    safe_res = evaluate_detections_against_ground_truth(
        detected_events=normal_dispatches,
        ground_truth_crashes=normal_crashes,
        video_duration_seconds=normal_duration,
    )
    safe_res["frame_count"] = normal_frames
    safe_res["candidate_count"] = len(normal_candidates)

    # 2. Collision clip evaluation
    crash_gt_info = gt_all.get("crash_demo.mp4", {})
    crash_duration = float(crash_gt_info.get("duration_seconds", 10.50))
    crash_frames = int(crash_gt_info.get("frame_count", 630))
    crash_crashes = crash_gt_info.get(
        "crashes", [{"start_s": 5.20, "end_s": 6.50, "label": "rear-end impact"}]
    )
    crash_vid_path = crash_gt_info.get("video_path", "data/videos/crash_demo.mp4")
    crash_traj_path = crash_gt_info.get("trajectory_path", "data/benchmarks/crash_trajectories.jsonl")

    crash_recs = load_or_generate_trajectories(
        crash_vid_path, crash_traj_path, force_live=force_live_tracking
    )
    crash_candidates, crash_dispatches = extract_clip_detections(crash_recs)

    crash_res = evaluate_detections_against_ground_truth(
        detected_events=crash_dispatches,
        ground_truth_crashes=crash_crashes,
        video_duration_seconds=crash_duration,
    )
    crash_res["frame_count"] = crash_frames
    crash_res["candidate_count"] = len(crash_candidates)
    crash_res["detection_timestamp"] = (
        crash_dispatches[0].get("evidence_timestamp_seconds") if crash_dispatches else None
    )

    return {
        "safe_traffic": safe_res,
        "collision_traffic": crash_res,
        "candidate_episodes_safe": len(normal_candidates),
        "candidate_episodes_crash": len(crash_candidates),
        "ground_truth_source": str(ground_truth_file or BENCHMARK_GT_FILE),
    }


def format_benchmark_table(evaluation_results):
    """Format benchmark evaluation metrics into clean GitHub-ready Markdown."""
    res = evaluation_results
    return fr"""### 📊 Empirical Ground-Truth Benchmark Results

| Metric | Measured Value | Standard Target | Interpretation |
| :--- | :---: | :---: | :--- |
| **Precision** | **{res['precision'] * 100:.1f}%** | > 80% | Ratio of true alerts to total candidate alerts |
| **Recall** | **{res['recall'] * 100:.1f}%** | > 85% | Ratio of detected accidents to actual accidents |
| **F1 Score** | **{res['f1_score']:.3f}** | > 0.82 | Harmonic mean of precision and recall |
| **Detection Delay** | **{res['mean_detection_delay_seconds']:.2f}s** | < 1.0s | Average latency from crash onset to trigger |
| **False Alarms / Hour** | **{res['false_alarms_per_hour']:.1f} FA/hr** | Low | Expected nuisance alerts per stream-hour |
"""


def format_dual_benchmark_markdown(results=None):
    r"""
    Format side-by-side benchmark comparison dynamically into clean Markdown table.
    Labels are constructed dynamically from numeric metrics without hardcoded success strings.
    """
    if results is None:
        results = run_standard_benchmark_suite()

    if not isinstance(results, dict) or "safe_traffic" not in results or "collision_traffic" not in results:
        raise ValueError("Invalid results dictionary supplied to format_dual_benchmark_markdown")

    s = results["safe_traffic"]
    c = results["collision_traffic"]

    s_dur = float(s["video_duration_seconds"])
    s_frames = int(s["frame_count"])
    c_dur = float(c["video_duration_seconds"])
    c_frames = int(c["frame_count"])

    s_gt = int(s["total_ground_truth_accidents"])
    c_gt = int(c["total_ground_truth_accidents"])

    s_tp = int(s["true_positives"])
    s_fp = int(s["false_positives"])
    s_fn = int(s["false_negatives"])

    c_tp = int(c["true_positives"])
    c_fp = int(c["false_positives"])
    c_fn = int(c["false_negatives"])

    s_cand = int(results.get("candidate_episodes_safe", s.get("candidate_count", 0)))
    c_cand = int(results.get("candidate_episodes_crash", c.get("candidate_count", 0)))

    s_prec = float(s["precision"]) * 100.0
    c_prec = float(c["precision"]) * 100.0
    s_rec = float(s["recall"]) * 100.0
    c_rec = float(c["recall"]) * 100.0
    s_f1 = float(s["f1_score"])
    c_f1 = float(c["f1_score"])

    s_fa_rate = float(s["false_alarms_per_hour"])
    c_fa_rate = float(c["false_alarms_per_hour"])

    # Safe traffic dispatch label
    s_disp = s_tp + s_fp
    if s_disp == 0:
        s_disp_label = "**0 (Zero False Dispatches)**"
    else:
        s_disp_label = f"**{s_disp} ({s_disp} False Dispatches)**"

    # Collision dispatch label
    c_det_ts = c.get("detection_timestamp")
    if c_tp > 0:
        ts_part = f" at {c_det_ts:.2f}s" if c_det_ts is not None else ""
        c_disp_label = f"**{c_tp} (Triggered{ts_part})**"
        c_recall_label = f"**{c_rec:.0f}% (Detected)**"
        c_cand_label = f"{c_cand} confirmed collision"
    else:
        c_disp_label = "**0 (MISSED - No Emergency Dispatch)**"
        c_recall_label = f"**{c_rec:.0f}% (MISSED)**"
        c_cand_label = f"{c_cand} unconfirmed candidate"

    s_recall_label = f"**{s_rec:.0f}% (0 missed)**" if s_fn == 0 else f"**{s_rec:.0f}% ({s_fn} missed)**"

    c_delay = c.get("mean_detection_delay_seconds")
    if c_tp > 0 and c_delay is not None:
        c_delay_label = f"**+{c_delay:.2f} seconds**"
    else:
        c_delay_label = "N/A (Missed)"

    return fr"""### 📊 Empirical Demonstration Evaluation Results

| Benchmark Dimension | Safe Highway Traffic (`normal.mp4`) | Real Collision Clip (`crash_demo.mp4`) | Target Standard |
| :--- | :---: | :---: | :--- |
| **Clip Duration** | {s_dur:.2f}s ({s_frames} frames) | {c_dur:.2f}s ({c_frames} frames) | Reference test clips |
| **Ground-Truth Collisions** | {s_gt} | {c_gt} (Onset: 5.20s) | Labeled ground truth |
| **Emergency Crash Dispatches** | {s_disp_label} | {c_disp_label} | Urgent responder alerts |
| **Candidate Triage Episodes** | {s_cand} monitoring episodes | {c_cand_label} | Sub-critical triage (analyst queue) |
| **Recall Rate** | {s_recall_label} | {c_recall_label} | $\ge 90\%$ |
| **Precision Rate** | **{s_prec:.0f}%** | **{c_prec:.0f}%** | $\ge 85\%$ |
| **F1 Score** | **{s_f1:.3f}** | **{c_f1:.3f}** | $\ge 0.85$ |
| **Mean Detection Delay** | N/A (No collision) | {c_delay_label} | $< 1.0$s latency |
| **Emergency False Alarms / Hr** | **{s_fa_rate:.1f} FA/hr** | {c_fa_rate:.1f} FA/hr | Emergency siren tier (zero nuisance) |
"""


def compute_confusion_matrix(
    detected_events,
    ground_truth_crashes,
    video_duration_seconds=60.0,
    total_negative_units=None,
    temporal_tolerance_seconds=1.5,
):
    r"""
    Compute a complete 2x2 confusion matrix (TP, FP, FN, TN) along with derived
    classification metrics: Accuracy, Sensitivity (Recall), Specificity, Precision, F1.
    """
    eval_res = evaluate_detections_against_ground_truth(
        detected_events=detected_events,
        ground_truth_crashes=ground_truth_crashes,
        video_duration_seconds=video_duration_seconds,
        temporal_tolerance_seconds=temporal_tolerance_seconds,
    )
    tp = eval_res["true_positives"]
    fp = eval_res["false_positives"]
    fn = eval_res["false_negatives"]

    # If total negative units (e.g. video frames or discrete intervals) is not given,
    # estimate based on video frames at standard 30 FPS
    if total_negative_units is None:
        total_units = int(video_duration_seconds * 30.0)
        total_negative_units = max(0, total_units - len(ground_truth_crashes))

    tn = max(0, total_negative_units - fp)
    total = tp + fp + fn + tn

    accuracy = (tp + tn) / total if total > 0 else 1.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 1.0
    sensitivity = eval_res["recall"]
    precision = eval_res["precision"]
    f1 = eval_res["f1_score"]

    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "matrix": [
            [tp, fp],
            [fn, tn],
        ],
        "accuracy": round(accuracy, 4),
        "specificity": round(specificity, 4),
        "sensitivity": round(sensitivity, 4),
        "precision": round(precision, 4),
        "f1_score": round(f1, 4),
        "false_alarms_per_hour": eval_res["false_alarms_per_hour"],
        "mean_detection_delay_seconds": eval_res["mean_detection_delay_seconds"],
        "total_samples": total,
    }


def filter_events_by_tuning(
    events,
    iou_thresh=0.05,
    max_ttc=3.5,
    max_norm_dist=1.8,
    min_closing_speed=5.0,
    require_contact=False,
):
    """
    Dynamically filter candidate interaction episodes based on calibrated threshold values.
    Used for real-time slider re-evaluation in the dashboard.
    """
    filtered = []
    for ev in events:
        iou = ev.get("peak_bbox_iou") or 0.0
        ttc = ev.get("minimum_ttc_seconds")
        norm_dist = ev.get("minimum_normalized_distance")
        closing_speed = ev.get("peak_closing_speed_px_per_second", 0.0)

        if require_contact:
            if iou >= iou_thresh:
                filtered.append(ev)
            continue

        if iou >= iou_thresh:
            filtered.append(ev)
            continue

        qualifies_ttc = ttc is not None and ttc <= max_ttc
        qualifies_dist = norm_dist is not None and norm_dist <= max_norm_dist

        if (qualifies_ttc or qualifies_dist) and closing_speed >= min_closing_speed:
            filtered.append(ev)

    return filtered


if __name__ == "__main__":
    import sys
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="MotionGuard Benchmark Evaluation Engine")
    parser.add_argument(
        "--ground-truth",
        dest="ground_truth",
        default=str(BENCHMARK_GT_FILE),
        help="Path to ground truth JSON file",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run live tracking on video clips instead of using cached trajectories",
    )
    args = parser.parse_args()

    suite_results = run_standard_benchmark_suite(
        ground_truth_file=args.ground_truth,
        force_live_tracking=args.live,
    )
    print(format_dual_benchmark_markdown(suite_results))
