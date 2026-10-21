import pytest
from pathlib import Path
from src.incident_pipeline import run_automated_incident_pipeline


def test_automated_pipeline_simulator(tmp_path, monkeypatch):
    import src.reporting
    import src.alert_dispatcher
    import src.incident_pipeline

    monkeypatch.setattr(src.reporting, "INCIDENT_LOG", tmp_path / "incidents.jsonl")
    monkeypatch.setattr(src.alert_dispatcher, "DISPATCH_LOG_PATH", tmp_path / "sms_dispatches.jsonl")
    monkeypatch.setattr(src.incident_pipeline, "INTERACTION_EVENTS_PATH", tmp_path / "events.jsonl")
    monkeypatch.setattr(src.incident_pipeline, "DOSSIERS_DIR", tmp_path / "incident_dossiers")

    video_path = Path("data/videos/normal.mp4")
    if not video_path.is_file():
        pytest.skip("normal.mp4 demo video not available for integration test.")

    result = run_automated_incident_pipeline(
        video_path=str(video_path),
        auto_dispatch=True,
        gateway_mode="SIMULATOR",
        recipient_phone="+919876543210",
        camera_name="Test Sector Junction",
        max_auto_alerts=1,
    )

    assert result["success"] is True
    assert result["critical_incidents_count"] >= 1
    assert len(result["incidents_created"]) >= 1

    first_incident = result["incidents_created"][0]
    assert "MG-" in first_incident["incident_id"]
    assert first_incident["pdf_path"] is not None
    assert Path(first_incident["pdf_path"]).is_file()

    assert first_incident["dispatch_result"] is not None
    assert first_incident["dispatch_result"]["success"] is True
    assert first_incident["dispatch_result"]["channel"] == "SMS_DISPATCH_SIMULATOR"


def test_extract_and_annotate_event_evidence(tmp_path):
    from src.video_processor import extract_and_annotate_event_evidence
    video_path = Path("data/videos/normal.mp4")
    if not video_path.is_file():
        pytest.skip("normal.mp4 demo video not available.")

    event = {
        "event_id": "TEST-EVT-01",
        "evidence_timestamp_seconds": 1.0,
        "track_ids": [1],
        "minimum_distance_px": 50.0,
        "peak_closing_speed_px_per_second": 20.0,
    }
    dummy_trajectories = [
        {
            "frame_index": 30,
            "timestamp_seconds": 1.0,
            "track_id": 1,
            "class_name": "car",
            "bbox_xyxy": [100.0, 100.0, 200.0, 200.0],
        }
    ]
    out_file = tmp_path / "test_annotated_frame.jpg"
    result_path = extract_and_annotate_event_evidence(
        video_path=video_path,
        event=event,
        trajectory_records=dummy_trajectories,
        output_path=out_file,
    )

    assert Path(result_path).is_file()
    assert Path(result_path).stat().st_size > 1000


if __name__ == "__main__":
    test_automated_pipeline_simulator(Path("."))
    print("Automated incident pipeline tests passed!")
