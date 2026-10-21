import pytest
from pathlib import Path
from src.video_processor import create_event_clip, inspect_video


def test_create_event_clip_normal_video():
    video_path = Path("data/videos/normal.mp4")
    if not video_path.is_file():
        pytest.skip("Test video normal.mp4 not found.")

    output_clip = Path("outputs/test_clips/test_clip_3s.mp4")
    output_clip.unlink(missing_ok=True)

    result = create_event_clip(
        video_path=video_path,
        timestamp_seconds=5.0,
        output_path=output_clip,
        window_seconds=1.5,
        event_id="PI-0001",
        severity_badge="🟡 NEAR-MISS",
        overlay_hud=True,
        reencode_h264=True,
    )

    assert Path(result["output_path"]).is_file()
    assert result["frames_written"] > 0
    assert result["duration_seconds"] > 0
    assert result["is_h264"] is True


def test_create_event_clip_negative_timestamp():
    video_path = Path("data/videos/normal.mp4")
    if not video_path.is_file():
        pytest.skip("Test video normal.mp4 not found.")

    with pytest.raises(ValueError, match="Timestamp cannot be negative"):
        create_event_clip(
            video_path=video_path,
            timestamp_seconds=-1.0,
            output_path="outputs/invalid.mp4",
        )
