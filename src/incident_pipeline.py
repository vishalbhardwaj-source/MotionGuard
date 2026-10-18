import json
import os
from pathlib import Path

from src.interaction_analysis import analyze_interactions
from src.event_aggregation import aggregate_interaction_events
from src.risk_engine import assess_event_risk
from src.reporting import create_incident_report
from src.pdf_report import create_interaction_pdf
from src.alert_dispatcher import format_emergency_sms, dispatch_sms, log_sms_dispatch
from src.video_processor import save_frame, extract_and_annotate_event_evidence


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
):
    """
    Fully automated end-to-end accident detection, emergency notification,
    incident logging, and forensic PDF dossier generation.

    When an accident/critical interaction is detected:
      1. Aggregates candidate interaction episodes.
      2. Pinpoints highest-risk collision events (small distance, high closing speed).
      3. Extracts and annotates the visual evidence snapshot.
      4. Automatically creates the official incident report.
      5. Automatically compiles the courtroom-ready PDF dossier.
      6. Automatically dispatches real-time smartphone alerts (Telegram / SMS).
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
        traj_file = OUTPUT_DIR / "uploaded_trajectories.jsonl"
        if not traj_file.exists():
            traj_file = OUTPUT_DIR / "trajectories_trails_test.jsonl"
        if traj_file.exists():
            records = []
            with traj_file.open("r", encoding="utf-8") as file:
                for line in file:
                    if line.strip():
                        records.append(json.loads(line))

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

    # Step 3: Analyze interactions and aggregate episodes
    findings = analyze_interactions(normalized_records)
    events = aggregate_interaction_events(findings)

    # Persist aggregated events
    with INTERACTION_EVENTS_PATH.open("w", encoding="utf-8") as file:
        for ev in events:
            file.write(json.dumps(ev) + "\n")

    if not events:
        return {
            "success": True,
            "message": "No anomalous interactions detected in video sequence.",
            "total_events_detected": 0,
            "incidents_created": [],
            "dispatches": [],
        }

    # Step 4: Identify critical incident candidates (High closing speed, close distance)
    # Sort primarily by smallest minimum distance, then highest closing speed
    sorted_events = sorted(
        events,
        key=lambda ev: (
            ev.get("minimum_distance_px", float("inf")),
            -ev.get("peak_closing_speed_px_per_second", 0.0),
        ),
    )

    # Select top critical candidates
    critical_candidates = []
    for ev in sorted_events:
        dist = ev.get("minimum_distance_px", float("inf"))
        closing = ev.get("peak_closing_speed_px_per_second", 0.0)
        conf_count = ev.get("peak_confirmation_count", 0)

        # Critical threshold: very close separation or high closing speed
        if (dist <= 20.0 and closing >= 20.0) or (dist <= 15.0) or (conf_count >= 3 and dist <= 30.0):
            critical_candidates.append(ev)

    # If no event met strict threshold, take the closest observed interaction
    if not critical_candidates and sorted_events:
        critical_candidates = [sorted_events[0]]

    # Limit auto-alerts to prevent flooding
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

        # 4e. Automatically dispatch emergency notification (Telegram / SMS)
        dispatch_res = None
        if auto_dispatch:
            sms_text = format_emergency_sms(
                event,
                camera_name=camera_name,
                incident_type="CRITICAL VEHICLE ACCIDENT / COLLISION DETECTED",
            )
            # Add live incident ID and dossier notice
            sms_text += f"\nIncident ID: {report['incident_id']}"
            sms_text += f"\nThreat Level: {risk_result['threat_level']} ({risk_result['threat_score']}/100)"

            dispatch_res = dispatch_sms(
                phone_number=recipient_phone,
                message_text=sms_text,
                gateway_mode=gateway_mode,
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
        })

    return {
        "success": True,
        "total_events_detected": len(events),
        "critical_incidents_count": len(incidents_created),
        "incidents_created": incidents_created,
        "dispatches": dispatches,
        "events": events,
    }
