from src.trajectory_analysis import analyze_trajectories


def make_record(frame, timestamp, track_id, bbox):
    return {
        "frame_index": frame,
        "timestamp_seconds": timestamp,
        "track_id": track_id,
        "class_name": "car",
        "bbox_xyxy": bbox,
    }


def test_trajectory_analysis():
    # The center stays fixed for three observations.
    stationary = [
        make_record(0, 0.0, 1, [10, 10, 30, 30]),
        make_record(1, 0.1, 1, [10, 10, 30, 30]),
        make_record(2, 0.2, 1, [10, 10, 30, 30]),
    ]
    result = analyze_trajectories(stationary)
    assert result[0]["displacement_px"] is None
    assert result[1]["displacement_px"] == 0
    assert result[2]["stationary_duration_seconds"] == 0.2

    # A 10-pixel horizontal shift over 0.1 seconds.
    moving = [
        make_record(0, 0.0, 2, [0, 0, 20, 20]),
        make_record(1, 0.1, 2, [10, 0, 30, 20]),
    ]
    result = analyze_trajectories(moving)
    assert result[1]["displacement_px"] == 10
    assert result[1]["image_speed_px_per_second"] == 100

    # A large gap must not be treated as continuous motion.
    missing = [
        make_record(0, 0.0, 3, [0, 0, 20, 20]),
        make_record(10, 1.0, 3, [100, 0, 120, 20]),
    ]
    result = analyze_trajectories(missing)
    assert result[1]["displacement_px"] is None
    assert result[1]["image_speed_px_per_second"] is None


if __name__ == "__main__":
    test_trajectory_analysis()
    print("All trajectory-analysis tests passed!")
