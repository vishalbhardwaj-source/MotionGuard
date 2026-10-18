import pytest
from pathlib import Path
from src.incident_pipeline import run_automated_incident_pipeline


def test_automated_pipeline_simulator(tmp_path):
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


if __name__ == "__main__":
    test_automated_pipeline_simulator(Path("."))
    print("Automated incident pipeline tests passed!")
