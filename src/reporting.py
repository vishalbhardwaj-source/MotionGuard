
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from src.db import save_incident_to_db, update_incident_status_in_db


OUTPUT_DIR = Path("outputs")
EVIDENCE_DIR = OUTPUT_DIR / "evidence"
INCIDENT_LOG = OUTPUT_DIR / "incidents.jsonl"


def create_incident_report(
    risk_result,
    scenario_id,
    timestamp_seconds,
    evidence_image,

    event_source="NO_COLLISION_EVENT",
    event_clip=None,
    track_id=None,
    vehicle_class=None,
):
    evidence_path = Path(evidence_image)

    if not evidence_path.is_file():
        raise FileNotFoundError(
            f"Evidence image not found: {evidence_path}"
        )

    if timestamp_seconds < 0:
        raise ValueError("Timestamp cannot be negative.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    incident_id = "MG-" + uuid4().hex[:8].upper()
    saved_evidence = EVIDENCE_DIR / f"{incident_id}.png"

    shutil.copy2(evidence_path, saved_evidence)

    report = {
        "incident_id": incident_id,
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "scenario_id": scenario_id,
        "timestamp_seconds": timestamp_seconds,
        "threat_score": risk_result["threat_score"],
        "threat_level": risk_result["threat_level"],
        "event_status": risk_result["event_status"],
        "speed_kmh": risk_result["speed_kmh"],
        "speed_limit_kmh": risk_result["speed_limit_kmh"],
        "speed_source": risk_result["speed_source"],
        "overspeed_ratio": risk_result["overspeed_ratio"],
        "reasons": risk_result["reasons"],
        "factor_breakdown": risk_result.get("factor_breakdown", []),

        "event_source": event_source,
        "track_id": track_id,
        "vehicle_class": vehicle_class,
        "evidence_image": str(saved_evidence),

        "event_clip": str(event_clip) if event_clip else None,
        "delivery_status": "SIMULATED_ONLY",
        "review_status": "NEW",
    }

    with INCIDENT_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(report) + "\n")

    try:
        save_incident_to_db(report)
    except Exception:
        pass

    return report



def update_review_status(incident_id, new_status):
    """Update an incident status and preserve its review history."""
    allowed_statuses = {"NEW", "UNDER REVIEW", "RESOLVED"}

    if new_status not in allowed_statuses:
        raise ValueError(f"Invalid review status: {new_status}")

    if not INCIDENT_LOG.exists():
        raise FileNotFoundError("Incident log does not exist.")

    reports = []
    found_report = None

    with INCIDENT_LOG.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            report = json.loads(line)

            if report.get("incident_id") == incident_id:
                if found_report is not None:
                    raise ValueError(
                        f"Duplicate incident ID in log: {incident_id}"
                    )

                found_report = report

            reports.append(report)

    if found_report is None:
        raise ValueError(f"Incident not found: {incident_id}")

    old_status = found_report.get("review_status", "NEW")
    now = datetime.now(timezone.utc).isoformat()

    # Preserve existing history; initialize it for older reports.
    history = found_report.get("review_history", [])

    if not history:
        history = [{
            "status": old_status,
            "changed_at": found_report.get("created_at_utc", now),
        }]

    # Record only actual status transitions.
    if old_status != new_status:
        history.append({
            "status": new_status,
            "changed_at": now,
        })

    found_report["review_status"] = new_status
    found_report["review_history"] = history
    found_report["review_status_updated_at"] = now

    temp_log = INCIDENT_LOG.with_suffix(".tmp")

    try:
        with temp_log.open("w", encoding="utf-8") as file:
            for report in reports:
                file.write(json.dumps(report) + "\n")

        temp_log.replace(INCIDENT_LOG)
    finally:
        if temp_log.exists():
            temp_log.unlink()

    try:
        update_incident_status_in_db(incident_id, new_status)
    except Exception:
        pass

    return found_report
