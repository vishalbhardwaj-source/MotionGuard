import json
from pathlib import Path
from PIL import Image

from src.risk_engine import assess_risk
from src.reporting import create_incident_report


def test_create_incident_report(tmp_path, monkeypatch):
    import src.reporting
    import src.db
    monkeypatch.setattr(src.reporting, "INCIDENT_LOG", tmp_path / "incidents.jsonl")
    monkeypatch.setattr(src.reporting, "EVIDENCE_DIR", tmp_path / "evidence")
    monkeypatch.setattr(src.db, "DEFAULT_DB_PATH", tmp_path / "test_motionguard.db")

    risk = assess_risk(
        speed_kmh=80,
        speed_limit_kmh=50,
    )

    evidence_path = tmp_path / "valid_test_frame.png"
    img = Image.new("RGB", (32, 32), color=(255, 0, 0))
    img.save(evidence_path, "PNG")

    report = create_incident_report(
        risk_result=risk,
        scenario_id="overspeed_demo",
        timestamp_seconds=5.0,
        evidence_image=str(evidence_path),
        event_source="NO_COLLISION_EVENT",
    )

    assert report["scenario_id"] == "overspeed_demo"
    assert report["threat_score"] == 60
    assert report["threat_level"] == "VERY HIGH"
    assert "incident_id" in report


def test_create_interaction_pdf_includes_thresholds_and_measured_values(tmp_path):
    from src.pdf_report import create_interaction_pdf
    event = {
        "event_id": "PI-0004",
        "evidence_timestamp_seconds": 6.61,
        "track_ids": [35, 83],
        "minimum_distance_px": 10.12,
        "peak_closing_speed_px_per_second": 54.68,
        "detection_count": 5,
        "peak_confirmation_count": 4,
    }
    pdf_bytes = create_interaction_pdf(event)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        test_create_incident_report(Path(td))
    print("\nReport generated successfully!")
