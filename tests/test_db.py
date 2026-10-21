import pytest
from pathlib import Path
from src.db import init_db, save_incident_to_db, update_incident_status_in_db, query_incidents_from_db, save_dispatch_to_db


def test_sqlite_incident_lifecycle(tmp_path):
    db_file = tmp_path / "test_motionguard.db"
    init_db(db_file)

    mock_report = {
        "incident_id": "MG-TEST-123",
        "scenario_id": "crash_test",
        "timestamp_seconds": 12.5,
        "threat_score": 95,
        "threat_level": "CRITICAL",
        "event_status": "SUSPECTED_COLLISION",
        "speed_kmh": 85.0,
        "speed_limit_kmh": 50.0,
        "overspeed_ratio": 0.70,
        "reasons": ["High speed", "Path conflict"],
        "factor_breakdown": [],
        "evidence_image": "outputs/evidence/test.png",
        "review_status": "NEW",
    }

    # Save incident
    save_incident_to_db(mock_report, db_path=db_file)
    results = query_incidents_from_db(db_path=db_file)
    assert len(results) == 1
    assert results[0]["incident_id"] == "MG-TEST-123"
    assert results[0]["threat_level"] == "CRITICAL"
    assert results[0]["review_status"] == "NEW"

    # Update review status
    update_incident_status_in_db("MG-TEST-123", "UNDER REVIEW", notes="Investigating footage", db_path=db_file)
    updated = query_incidents_from_db(status="UNDER REVIEW", db_path=db_file)
    assert len(updated) == 1
    assert updated[0]["review_status"] == "UNDER REVIEW"
    assert len(updated[0]["review_history"]) == 1
    assert updated[0]["review_history"][0]["previous_status"] == "NEW"


def test_sqlite_dispatch_logging(tmp_path):
    db_file = tmp_path / "test_motionguard.db"
    mock_dispatch = {
        "message_id": "TG-9999",
        "channel": "TELEGRAM_ALERT",
        "status": "DELIVERED",
        "recipient": "Chat ID: 12345",
        "carrier_network": "Telegram Bot API",
        "dispatched_at": "2026-10-21T12:00:00Z",
        "body": "Collision alert at CAM-01",
        "photo_attached": True,
    }
    save_dispatch_to_db(mock_dispatch, db_path=db_file)
    assert db_file.is_file()
