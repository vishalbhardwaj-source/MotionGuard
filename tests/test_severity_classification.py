import pytest
from src.risk_engine import classify_severity, assess_event_risk


def test_classify_severity_collision():
    # IoU overlap >= 0.05
    event = {
        "event_id": "CRASH-001",
        "peak_bbox_iou": 0.12,
        "minimum_distance_px": 8.5,
        "post_impact_signals": ["POST_IMPACT_VELOCITY_DROP"],
    }
    sev = classify_severity(event)
    assert sev["category"] == "COLLISION"
    assert "🔴" in sev["badge"]
    assert sev["priority"] == 1
    assert sev["dispatch_eligible"] is True
    assert "Immediate Priority 1" in sev["recommended_action"]


def test_classify_severity_near_miss():
    # Tight optical TTC and normalized distance, but NO bounding box overlap
    event = {
        "event_id": "NEAR-001",
        "peak_bbox_iou": 0.0,
        "minimum_distance_px": 28.0,
        "minimum_ttc_seconds": 1.4,
        "minimum_normalized_distance": 0.85,
        "peak_closing_speed_px_per_second": 32.0,
        "post_impact_signals": [],
    }
    sev = classify_severity(event)
    assert sev["category"] == "NEAR_MISS"
    assert "🟡" in sev["badge"]
    assert sev["priority"] == 3
    assert sev["dispatch_eligible"] is False
    assert "Near-Miss Safety Heatmap" in sev["recommended_action"]


def test_classify_severity_stopped_vehicle():
    event = {
        "event_id": "STOP-001",
        "is_stopped_vehicle": True,
        "stopped_duration_seconds": 4.5,
        "peak_bbox_iou": 0.0,
        "post_impact_signals": [],
    }
    sev = classify_severity(event)
    assert sev["category"] == "STOPPED_VEHICLE"
    assert "🟠" in sev["badge"]
    assert sev["priority"] == 2
    assert sev["dispatch_eligible"] is True
    assert "Tow Patrol" in sev["recommended_action"]


def test_classify_severity_nominal():
    event = {
        "event_id": "NOM-001",
        "peak_bbox_iou": 0.0,
        "minimum_distance_px": 120.0,
        "minimum_ttc_seconds": 8.0,
        "minimum_normalized_distance": 4.2,
        "peak_closing_speed_px_per_second": 4.0,
    }
    sev = classify_severity(event)
    assert sev["category"] == "NOMINAL"
    assert "🟢" in sev["badge"]
    assert sev["priority"] == 4
    assert sev["dispatch_eligible"] is False


def test_assess_event_risk_with_severity():
    event = {
        "event_id": "CRASH-TEST",
        "peak_bbox_iou": 0.08,
        "minimum_distance_px": 5.0,
        "peak_closing_speed_px_per_second": 45.0,
        "detection_count": 5,
        "peak_confirmation_count": 4,
    }
    risk = assess_event_risk(event)
    assert "severity" in risk
    assert risk["severity"]["category"] == "COLLISION"
    assert risk["threat_level"] == "CRITICAL"
