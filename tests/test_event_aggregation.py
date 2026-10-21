
from src.event_aggregation import aggregate_interaction_events


def make_finding(time, pair=(1, 2), distance=50, closing=10):
    return {
        "timestamp_seconds": time,
        "track_ids": list(pair),
        "distance_px": distance,
        "closing_speed_px_per_second": closing,
        "finding": "POTENTIAL_APPROACHING_INTERACTION",
    }


def test_repeated_findings_are_grouped():
    findings = [
        make_finding(1.0, distance=40, closing=12),
        make_finding(1.1, distance=35, closing=15),
        make_finding(1.2, distance=30, closing=11),
    ]

    events = aggregate_interaction_events(findings)

    assert len(events) == 1
    assert events[0]["detection_count"] == 3
    assert events[0]["minimum_distance_px"] == 30
    assert events[0]["peak_closing_speed_px_per_second"] == 15
    assert events[0]["evidence_timestamp_seconds"] == 1.2
    assert events[0]["minimum_distance_timestamp_seconds"] == 1.2
    assert events[0]["peak_closing_speed_timestamp_seconds"] == 1.1
    print("PASS: repeated findings become one event")


def test_large_gap_splits_events():
    findings = [
        make_finding(1.0),
        make_finding(1.2),
        make_finding(3.0),
    ]

    events = aggregate_interaction_events(findings)

    assert len(events) == 2
    assert events[0]["detection_count"] == 2
    assert events[1]["detection_count"] == 1
    print("PASS: large time gaps create separate events")


def test_different_pairs_remain_separate():
    findings = [
        make_finding(1.0, pair=(1, 2)),
        make_finding(1.1, pair=(3, 4)),
    ]

    events = aggregate_interaction_events(findings)

    assert len(events) == 2
    print("PASS: different object pairs remain separate")


def test_empty_input():
    assert aggregate_interaction_events([]) == []
    print("PASS: empty input returns no events")


if __name__ == "__main__":
    test_repeated_findings_are_grouped()
    test_large_gap_splits_events()
    test_different_pairs_remain_separate()
    test_empty_input()
    print("\nAll event-aggregation tests passed!")
