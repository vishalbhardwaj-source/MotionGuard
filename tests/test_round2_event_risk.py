import math
import pytest
from pathlib import Path
from src.risk_engine import (
    assess_event_risk,
    IMAGE_SPACE_RISK_THRESHOLDS,
    EVENT_RISK_THRESHOLDS,
)
from src.prune_gateway import (
    prune_nominal_candidates,
    generate_prune_triage_summary,
)


def test_happy_path_strong_event_pi_0004():
    """
    Acceptance Row 1: Happy path, strong event.
    The PI-0004 event: 10.12 px, 54.68 px/s, detection count 5, confirmation count 4.
    Expected: Score 100, level CRITICAL, Close proximity and Rapid approach both read 'detected'.
    """
    event = {
        "event_id": "PI-0004",
        "minimum_distance_px": 10.12,
        "peak_closing_speed_px_per_second": 54.68,
        "detection_count": 5,
        "peak_confirmation_count": 4,
        "duration_seconds": 1.5,
    }
    result = assess_event_risk(event)
    assert result["threat_score"] == 100
    assert result["threat_level"] == "CRITICAL"

    breakdown = {item["factor"]: item["status"] for item in result["factor_breakdown"]}
    assert breakdown["Close proximity"] == "detected"
    assert breakdown["Rapid approach"] == "detected"

    # Factor cards must state measured values and thresholds
    for card in result["factor_breakdown"]:
        assert "px" in card["detail"] or "frames" in card["detail"]
        assert "threshold" in card["detail"].lower()


def test_happy_path_weak_event():
    """
    Acceptance Row 2: Happy path, weak event.
    60.0 px, 8.0 px/s, detection count 1, confirmation count 3.
    Expected: Scores strictly lower than PI-0004 and below CRITICAL.
    """
    event = {
        "event_id": "PI-WEAK",
        "minimum_distance_px": 60.0,
        "peak_closing_speed_px_per_second": 8.0,
        "detection_count": 1,
        "peak_confirmation_count": 3,
        "duration_seconds": 0.8,
    }
    result = assess_event_risk(event)
    assert result["threat_score"] < 100
    assert result["threat_level"] != "CRITICAL"
    assert result["threat_level"] in ["LOW", "ELEVATED", "HIGH"]


def test_ordering_monotonicity_grid():
    """
    Acceptance Row 3: Ordering.
    A grid of at least 5 distances by 5 closing speeds, other fields fixed.
    Expected: A smaller distance or a larger closing speed never lowers the score.
    """
    distances = [5.0, 15.0, 30.0, 55.0, 90.0]  # strictly increasing distances
    speeds = [4.0, 12.0, 25.0, 40.0, 65.0]     # strictly increasing closing speeds

    # Fixed baseline fields
    fixed_fields = {
        "detection_count": 3,
        "peak_confirmation_count": 2,
        "duration_seconds": 1.0,
    }

    # Build score grid: grid[d_idx][s_idx]
    grid = []
    for d in distances:
        row = []
        for s in speeds:
            ev = dict(fixed_fields)
            ev["minimum_distance_px"] = d
            ev["peak_closing_speed_px_per_second"] = s
            risk = assess_event_risk(ev)
            row.append(risk["threat_score"])
        grid.append(row)

    # 1. Monotonicity along speed axis: for any distance row, larger closing speed never lowers score
    for r_idx, row in enumerate(grid):
        for c in range(len(row) - 1):
            assert row[c + 1] >= row[c], (
                f"Speed monotonicity violated at distance {distances[r_idx]} px: "
                f"speed {speeds[c]} -> {row[c]}, speed {speeds[c+1]} -> {row[c+1]}"
            )

    # 2. Monotonicity along distance axis: for any speed column, smaller distance never lowers score
    for c_idx in range(len(speeds)):
        for r in range(len(distances) - 1):
            # distances[r] < distances[r+1], so smaller distance (row r) must have score >= row r+1
            assert grid[r][c_idx] >= grid[r + 1][c_idx], (
                f"Distance monotonicity violated at speed {speeds[c_idx]} px/s: "
                f"distance {distances[r]} -> {grid[r][c_idx]}, distance {distances[r+1]} -> {grid[r+1][c_idx]}"
            )


def test_pixel_only_text_no_kmh():
    """
    Acceptance Row 4: Pixel-only text.
    Four sample events across the score range.
    Expected: No returned string contains 'km/h', 'speed limit' or 'above the limit' in any letter case.
    """
    forbidden_phrases = ["km/h", "speed limit", "above the limit", "over the limit"]

    sample_events = [
        {"minimum_distance_px": 8.0, "peak_closing_speed_px_per_second": 55.0, "detection_count": 5, "peak_confirmation_count": 4},
        {"minimum_distance_px": 22.0, "peak_closing_speed_px_per_second": 32.0, "detection_count": 3, "peak_confirmation_count": 3},
        {"minimum_distance_px": 48.0, "peak_closing_speed_px_per_second": 14.0, "detection_count": 2, "peak_confirmation_count": 2},
        {"minimum_distance_px": 85.0, "peak_closing_speed_px_per_second": 3.0, "detection_count": 1, "peak_confirmation_count": 1},
    ]

    for ev in sample_events:
        risk = assess_event_risk(ev)

        # Collect all string fields
        strings_to_check = [
            risk.get("threat_level", ""),
            risk.get("event_status", ""),
            risk.get("explainability_summary", ""),
        ]
        strings_to_check.extend(risk.get("reasons", []))
        for card in risk.get("factor_breakdown", []):
            strings_to_check.extend([
                card.get("factor", ""),
                card.get("status", ""),
                card.get("display_status", ""),
                card.get("detail", ""),
                card.get("badge", ""),
            ])

        for text in strings_to_check:
            text_lower = str(text).lower()
            for phrase in forbidden_phrases:
                assert phrase not in text_lower, f"Forbidden phrase '{phrase}' found in string: '{text}'"


def test_edge_missing_data():
    """
    Acceptance Row 5: Edge: missing data.
    An event with no minimum_distance_px, or an empty event.
    Expected: Returns LOW, with the proximity factor marked 'insufficient data'; no exception.
    """
    # 1. Event with no minimum_distance_px
    ev_no_dist = {
        "event_id": "EVT-MISSING-DIST",
        "peak_closing_speed_px_per_second": 20.0,
        "detection_count": 2,
    }
    res1 = assess_event_risk(ev_no_dist)
    assert res1["threat_level"] == "LOW"
    assert res1["threat_score"] <= 20
    breakdown1 = {item["factor"]: item["status"] for item in res1["factor_breakdown"]}
    assert breakdown1["Close proximity"] == "insufficient data"

    # 2. Empty event
    res2 = assess_event_risk({})
    assert res2["threat_level"] == "LOW"
    breakdown2 = {item["factor"]: item["status"] for item in res2["factor_breakdown"]}
    assert breakdown2["Close proximity"] == "insufficient data"

    # 3. None input
    res3 = assess_event_risk(None)
    assert res3["threat_level"] == "LOW"


def test_failure_bad_values():
    """
    Acceptance Row 6: Failure: bad values.
    A boolean, NaN, negative or non-numeric distance or closing speed.
    Expected: Raises ValueError, in the style of assess_risk.
    """
    # Boolean values
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": True, "peak_closing_speed_px_per_second": 10.0})
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": 10.0, "peak_closing_speed_px_per_second": False})

    # NaN values
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": float("nan"), "peak_closing_speed_px_per_second": 10.0})
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": 10.0, "peak_closing_speed_px_per_second": float("nan")})

    # Negative values
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": -5.0, "peak_closing_speed_px_per_second": 10.0})
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": 10.0, "peak_closing_speed_px_per_second": -2.0})

    # Non-numeric and numeric string values (must raise ValueError, not crash or convert)
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": "invalid", "peak_closing_speed_px_per_second": 10.0})
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": "12", "peak_closing_speed_px_per_second": 10.0})
    with pytest.raises(ValueError):
        assess_event_risk({"minimum_distance_px": 12.0, "peak_closing_speed_px_per_second": "15.5"})


def test_alert_wording_simulator_no_confirmed_collision(tmp_path, monkeypatch):
    """
    Acceptance Row 7: Alert wording.
    The automatic pipeline run with the SIMULATOR gateway.
    Expected: The alert text includes the threat level and the word 'candidate' or 'review',
    and does NOT contain 'COLLISION DETECTED'.
    """
    import src.reporting
    import src.alert_dispatcher
    import src.incident_pipeline
    import src.db
    from src.incident_pipeline import run_automated_incident_pipeline

    monkeypatch.setattr(src.reporting, "INCIDENT_LOG", tmp_path / "incidents.jsonl")
    monkeypatch.setattr(src.reporting, "EVIDENCE_DIR", tmp_path / "evidence")
    monkeypatch.setattr(src.incident_pipeline, "EVIDENCE_DIR", tmp_path / "evidence")
    monkeypatch.setattr(src.alert_dispatcher, "DISPATCH_LOG_PATH", tmp_path / "sms_dispatches.jsonl")
    monkeypatch.setattr(src.incident_pipeline, "INTERACTION_EVENTS_PATH", tmp_path / "events.jsonl")
    monkeypatch.setattr(src.incident_pipeline, "DOSSIERS_DIR", tmp_path / "incident_dossiers")
    monkeypatch.setattr(src.db, "DEFAULT_DB_PATH", tmp_path / "test_motionguard.db")

    video_path = Path("data/videos/crash_demo.mp4")
    if not video_path.is_file():
        pytest.skip("crash_demo.mp4 demo video not available for integration test.")

    # Load benchmark trajectories
    traj_path = Path("data/benchmarks/crash_trajectories.jsonl")
    records = None
    if traj_path.is_file():
        import json
        records = [json.loads(l) for l in traj_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    result = run_automated_incident_pipeline(
        video_path=str(video_path),
        trajectory_records=records,
        auto_dispatch=True,
        gateway_mode="SIMULATOR",
        recipient_phone="+919876543210",
        camera_name="Highway Sector 4",
        max_auto_alerts=1,
    )

    assert result["success"] is True
    assert len(result["dispatches"]) >= 1

    first_dispatch = result["dispatches"][0]
    sent_text = first_dispatch.get("body") or first_dispatch.get("message", "")

    # Verify: Must contain threat level (CRITICAL, HIGH, etc.)
    assert any(lvl in sent_text for lvl in ["CRITICAL", "HIGH", "VERY HIGH", "ELEVATED", "LOW"])

    # Verify: Must contain 'candidate' or 'review' (case-insensitive)
    sent_text_lower = sent_text.lower()
    assert "candidate" in sent_text_lower or "review" in sent_text_lower

    # Verify: Must NOT contain 'COLLISION DETECTED'
    assert "COLLISION DETECTED" not in sent_text


def test_prune_integration():
    """
    Verify Prune integration:
      1. prune_nominal_candidates prunes low-threat background noise.
      2. generate_prune_triage_summary functions deterministically in SIMULATOR mode.
    """
    events = [
        {"event_id": "EVT-CRIT", "minimum_distance_px": 10.0, "peak_closing_speed_px_per_second": 50.0, "detection_count": 5, "peak_confirmation_count": 4},
        {"event_id": "EVT-NOISE", "minimum_distance_px": 95.0, "peak_closing_speed_px_per_second": 1.0, "detection_count": 1, "peak_confirmation_count": 1},
    ]

    pruned = prune_nominal_candidates(events, min_threat_score=40.0)
    assert len(pruned) == 1
    assert pruned[0]["event_id"] == "EVT-CRIT"

    # Check simulator triage summary
    risk = assess_event_risk(pruned[0])
    summary = generate_prune_triage_summary(pruned[0], risk, gateway_mode="SIMULATOR")
    assert summary["status"] == "SIMULATED"
    assert summary["gateway"] == "PRUNE_SIMULATOR"
    assert "EVT-CRIT" in summary["triage_summary"]
    assert "px" in summary["triage_summary"]
