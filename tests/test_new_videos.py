import json
from pathlib import Path
import pytest
from src.incident_pipeline import run_automated_incident_pipeline


def test_new_video_cctv1_detection():
    """Verify that new video CCTV1 detects incidents and stopped hazards."""
    video_path = Path("data/videos/CCTV1.mp4")
    traj_path = Path("data/benchmarks/cctv1_trajectories.jsonl")
    if not video_path.is_file() or not traj_path.is_file():
        pytest.skip("CCTV1 files not available.")

    records = [json.loads(line) for line in traj_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    result = run_automated_incident_pipeline(
        video_path=str(video_path),
        trajectory_records=records,
        auto_dispatch=False,
    )
    assert result["success"] is True
    assert result["total_events_detected"] >= 1
    assert len(result["incidents_created"]) >= 1

    first_inc = result["incidents_created"][0]
    assert first_inc["threat_score"] >= 40
    assert first_inc["threat_level"] in ("ELEVATED", "HIGH", "CRITICAL")


def test_new_video_cctv2_detection():
    """Verify that new video CCTV2 detects vehicle interactions and proximity events."""
    video_path = Path("data/videos/CCTV2.mp4")
    traj_path = Path("data/benchmarks/cctv2_trajectories.jsonl")
    if not video_path.is_file() or not traj_path.is_file():
        pytest.skip("CCTV2 files not available.")

    records = [json.loads(line) for line in traj_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    result = run_automated_incident_pipeline(
        video_path=str(video_path),
        trajectory_records=records,
        auto_dispatch=False,
    )
    assert result["success"] is True
    assert result["total_events_detected"] >= 1
    assert len(result["incidents_created"]) >= 1

    first_inc = result["incidents_created"][0]
    assert first_inc["threat_score"] >= 40
    assert first_inc["threat_level"] in ("ELEVATED", "HIGH", "CRITICAL")
