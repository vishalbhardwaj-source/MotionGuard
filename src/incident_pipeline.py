import json
import os
from pathlib import Path

from src.interaction_analysis import analyze_interactions
from src.event_aggregation import aggregate_interaction_events
from src.risk_engine import assess_event_risk, is_emergency_dispatch_eligible
from src.reporting import create_incident_report
from src.pdf_report import create_interaction_pdf
from src.alert_dispatcher import format_emergency_sms, dispatch_sms, log_sms_dispatch
from src.video_processor import save_frame, extract_and_annotate_event_evidence
from src.config import load_config


OUTPUT_DIR = Path("outputs")
EVIDENCE_DIR = OUTPUT_DIR / "evidence"
DOSSIERS_DIR = OUTPUT_DIR / "incident_dossiers"
INTERACTION_EVENTS_PATH = OUTPUT_DIR / "interaction_events_test.jsonl"


def run_automated_incident_pipeline(
    video_path,
    trajectory_records=None,
    auto_dispatch=True,
    gateway_mode="AUTO",
    recipient_phone="+919876543210",
    camera_name="Highway North - Sector 4",
    max_auto_alerts=2,
    proximity_threshold_px=None,
    min_closing_speed_px_s=None,
    min_consecutive_matches=None,
    max_gap_seconds=None,
):
    """
    Fully automated end-to-end accident detection, emergency notification,
    incident logging, and forensic PDF dossier generation.

    When an accident/critical interaction is detected:
      1. Aggregates candidate interaction episodes.
      2. Pinpoints highest-risk collision events (small distance, high closing speed).
      3. Extracts and annotates the visual evidence snapshot.
      4. Automatically creates the official incident report.
      5. Automatically compiles the forensic decision-support PDF dossier.
      6. Dispatches real-time smartphone alerts (Telegram with snapshot / SMS) with cooldown rate-limiting.
    """
    video_file = Path(video_path)
    if not video_file.is_file():
        raise FileNotFoundError(f"Video file not found: {video_file}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    DOSSIERS_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load or derive trajectory records
    records = trajectory_records
    if not records:
        for candidate in (
            OUTPUT_DIR / "uploaded_trajectories.jsonl",
            OUTPUT_DIR / "trajectories_trails_test.jsonl",
            Path("data/sample_trajectories.jsonl"),
        ):
            if candidate.exists():
                records = []
                with candidate.open("r", encoding="utf-8") as file:
                    for line in file:
                        if line.strip():
                            records.append(json.loads(line))
                if records:
                    break

    if not records:
        return {
            "success": False,
            "error": "No trajectory records available. Please run video tracking first.",
            "incidents_created": [],
            "dispatches": [],
        }

    # Step 2: Ensure center_xy is present in records
    normalized_records = []
    for r in records:
        rec = dict(r)
        if "center_xy" not in rec and "bbox_xyxy" in rec:
            x1, y1, x2, y2 = rec["bbox_xyxy"]
            rec["center_xy"] = [(x1 + x2) / 2, (y1 + y2) / 2]
        normalized_records.append(rec)

    # Step 3: Analyze interactions and aggregate episodes with config-driven heuristics
    cfg = load_config()
    k_cfg = cfg.get("kinematics", {})

    # Adaptive proximity scaling based on video resolution for new videos (FullHD / 4K)
    if proximity_threshold_px is not None:
        effective_proximity = proximity_threshold_px
    else:
        base_prox = k_cfg.get("proximity_threshold_px", 80.0)
        try:
            from src.video_processor import inspect_video
            info = inspect_video(video_file)
            width = info.get("width", 1280)
            if width > 1280:
                effective_proximity = round(base_prox * (width / 1280.0), 1)
            else:
                effective_proximity = base_prox
        except Exception:
            effective_proximity = base_prox

    findings = analyze_interactions(
        normalized_records,
        proximity_threshold_px=effective_proximity,
        min_closing_speed_px_s=min_closing_speed_px_s if min_closing_speed_px_s is not None else k_cfg.get("min_closing_speed_px_s", 5.0),
        max_gap_seconds=max_gap_seconds if max_gap_seconds is not None else k_cfg.get("max_gap_seconds", 0.3),
        min_consecutive_matches=min_consecutive_matches if min_consecutive_matches is not None else k_cfg.get("min_consecutive_matches", 2),
        max_ttc_seconds=k_cfg.get("max_ttc_seconds", 3.5),
        max_normalized_distance=k_cfg.get("max_normalized_distance", 1.8),
    )
    events = aggregate_interaction_events(findings)

    # Check if any vehicle experienced a prolonged stationary hazard (>2s) or single-vehicle obstruction
    if not events:
        try:
            from src.trajectory_analysis import analyze_trajectories
            traj_motion = analyze_trajectories(normalized_records)
            stopped_tracks = {}
            for item in traj_motion:
                dur = item.get("stationary_duration_seconds", 0.0)
                if dur >= 2.0:
                    tid = item["track_id"]
                    if tid not in stopped_tracks or dur > stopped_tracks[tid]["stationary_duration_seconds"]:
                        stopped_tracks[tid] = item
            for tid, s_item in stopped_tracks.items():
                ev_id = f"PI-SOLO-{tid}"
                events.append({
                    "event_id": ev_id,
                    "track_ids": [tid],
                    "start_seconds": max(0.0, s_item["timestamp_seconds"] - s_item["stationary_duration_seconds"]),
                    "end_seconds": s_item["timestamp_seconds"],
                    "duration_seconds": round(s_item["stationary_duration_seconds"], 2),
                    "detection_count": 5,
                    "contact_frame_count": 0,
                    "peak_confirmation_count": 3,
                    "minimum_distance_px": 0.0,
                    "minimum_distance_timestamp_seconds": s_item["timestamp_seconds"],
                    "peak_closing_speed_px_per_second": 0.0,
                    "peak_closing_speed_timestamp_seconds": s_item["timestamp_seconds"],
                    "minimum_ttc_seconds": None,
                    "optical_tau_ttc_seconds": None,
                    "minimum_normalized_distance": 0.0,
                    "peak_bbox_iou": 0.0,
                    "post_impact_signals": ["STATIONARY_HAZARD"],
                    "evidence_timestamp_seconds": s_item["timestamp_seconds"],
                    "is_stopped_vehicle": True,
                    "stopped_duration_seconds": round(s_item["stationary_duration_seconds"], 2),
                    "finding": "STOPPED_VEHICLE_OBSTRUCTION",
                })
        except Exception:
            pass

    # Persist aggregated events
    with INTERACTION_EVENTS_PATH.open("w", encoding="utf-8") as file:
        for ev in events:
            file.write(json.dumps(ev) + "\n")

    if not events:
        return {
            "success": True,
            "message": "No anomalous interactions detected in video sequence.",
            "total_events_detected": 0,
            "critical_incidents_count": 0,
            "events": [],
            "incidents_created": [],
            "dispatches": [],
        }

    # Step 4: Identify critical incident candidates using canonical emergency qualification rule
    sorted_events = sorted(
        events,
        key=lambda ev: (
            ev.get("minimum_distance_px", float("inf")),
            -ev.get("peak_closing_speed_px_per_second", 0.0),
        ),
    )

    # Use unified canonical rule to identify verified collision events eligible for emergency siren/SMS dispatch
    critical_candidates = [ev for ev in sorted_events if is_emergency_dispatch_eligible(ev)]

    # If no event met strict emergency dispatch threshold, prioritize highest-risk candidate for analyst triage logging
    if not critical_candidates and sorted_events:
        candidates_to_process = [sorted_events[0]]
    else:
        candidates_to_process = critical_candidates[:max_auto_alerts]

    incidents_created = []
    dispatches = []

    for event in candidates_to_process:
        event_id = event.get("event_id", "EVT-UNKNOWN")
        timestamp = event.get("evidence_timestamp_seconds", event.get("start_seconds", 0.0))

        # 4a. Assess risk and explainable factor breakdown
        risk_result = assess_event_risk(event)

        # 4b. Extract visual evidence snapshot
        evidence_image_path = EVIDENCE_DIR / f"{event_id}_evidence.jpg"
        try:
            valid_evidence = extract_and_annotate_event_evidence(
                video_path=video_file,
                event=event,
                trajectory_records=records,
                output_path=evidence_image_path,
            )
        except Exception:
            try:
                save_frame(video_file, timestamp, evidence_image_path)
                valid_evidence = str(evidence_image_path)
            except Exception:
                fallback_evidence = OUTPUT_DIR / "evidence" / "test_frame.png"
                valid_evidence = str(fallback_evidence) if fallback_evidence.is_file() else str(video_file)

        # 4c. Create official incident report in incidents.jsonl
        report = create_incident_report(
            risk_result=risk_result,
            scenario_id=f"auto_video_detection_{event_id}",
            timestamp_seconds=round(float(timestamp), 2),
            evidence_image=valid_evidence,
            event_source=f"AUTONOMOUS_VIDEO_PIPELINE_{event_id}",
            track_id=", ".join(map(str, event.get("track_ids", []))),
            vehicle_class="Motorized Vehicle Interaction",
        )

        # 4d. Automatically generate official forensic PDF dossier
        pdf_path = DOSSIERS_DIR / f"{event_id}_investigation_dossier.pdf"
        try:
            pdf_bytes = create_interaction_pdf(event, evidence_path=valid_evidence)
            pdf_path.write_bytes(pdf_bytes)
        except Exception as pdf_err:
            print(f"Warning: PDF compilation warning for {event_id}: {pdf_err}")

        # 4e. Automatically dispatch emergency notification (Telegram / SMS) ONLY if event meets canonical emergency qualification
        dispatch_res = None
        should_dispatch = auto_dispatch and is_emergency_dispatch_eligible(event)
        if should_dispatch:
            candidate_label = f"INCIDENT CANDIDATE [{risk_result['threat_level']}] - HUMAN REVIEW REQUIRED"
            dossier_link = os.getenv("DOSSIER_URL") or os.getenv("INVESTIGATION_DOSSIER_URL") or "http://localhost:8501"
            sms_text = format_emergency_sms(
                event,
                camera_name=camera_name,
                camera_id="CAM-01",
                incident_type=candidate_label,
                incident_id=report["incident_id"],
                threat_level=risk_result["threat_level"],
                threat_score=risk_result["threat_score"],
                dossier_link=dossier_link,
            )

            dispatch_res = dispatch_sms(
                phone_number=recipient_phone,
                message_text=sms_text,
                photo_path=valid_evidence,
                camera_id="CAM-01",
                gateway_mode=gateway_mode,
                dossier_link=dossier_link,
            )
            log_sms_dispatch(dispatch_res)
            dispatches.append(dispatch_res)

        incidents_created.append({
            "event_id": event_id,
            "incident_id": report["incident_id"],
            "timestamp": timestamp,
            "threat_score": risk_result["threat_score"],
            "threat_level": risk_result["threat_level"],
            "factor_breakdown": risk_result.get("factor_breakdown", []),
            "evidence_image": valid_evidence,
            "pdf_path": str(pdf_path) if pdf_path.is_file() else None,
            "dispatch_result": dispatch_res,
            "emergency_dispatch_eligible": should_dispatch,
        })

    return {
        "success": True,
        "total_events_detected": len(events),
        "critical_incidents_count": len(critical_candidates),
        "incidents_created": incidents_created,
        "dispatches": dispatches,
        "events": events,
    }
