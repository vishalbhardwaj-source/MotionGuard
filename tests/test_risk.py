from src.risk_engine import assess_risk, assess_event_risk

tests = [
    (45, 50, False, 10),
    (50, 50, False, 10),
    (55, 50, False, 20),
    (60, 50, False, 40),
    (75, 50, False, 60),
    (50, 50, True, 100),
]

def test_assess_risk():
    for speed, limit, collision, expected in tests:
        result = assess_risk(speed, limit, collision)
        actual = result["threat_score"]

        assert actual == expected, (
            f"Expected {expected}, got {actual}"
        )
        assert "factor_breakdown" in result
        assert len(result["factor_breakdown"]) == 4
        assert "explainability_summary" in result


def test_explainable_risk_breakdown_collision():
    result = assess_risk(speed_kmh=80, speed_limit_kmh=50, suspected_collision=True)
    assert result["threat_score"] == 100
    assert result["threat_level"] == "CRITICAL"

    breakdown = {item["factor"]: item["status"] for item in result["factor_breakdown"]}
    assert breakdown["Potential path conflict"] == "detected"
    assert breakdown["Close proximity"] == "detected"
    assert breakdown["Rapid approach"] == "insufficient data"
    assert breakdown["Collision confirmation"] == "unavailable"

    # Verify bullet strings in reasons
    reasons_text = " ".join(result["reasons"])
    assert "Potential path conflict: detected." in reasons_text
    assert "Close proximity: detected." in reasons_text
    assert "Rapid approach: insufficient data." in reasons_text
    assert "Collision confirmation: unavailable." in reasons_text


def test_explainable_risk_breakdown_nominal():
    result = assess_risk(speed_kmh=45, speed_limit_kmh=50, suspected_collision=False)
    assert result["threat_score"] == 10
    assert result["threat_level"] == "LOW"

    breakdown = {item["factor"]: item["status"] for item in result["factor_breakdown"]}
    assert breakdown["Potential path conflict"] == "clear"
    assert breakdown["Close proximity"] == "clear"
    assert breakdown["Rapid approach"] == "nominal"
    assert breakdown["Collision confirmation"] == "not indicated"


def test_assess_event_risk():
    mock_event = {
        "event_id": "PI-0004",
        "minimum_distance_px": 10.12,
        "peak_closing_speed_px_per_second": 54.68,
        "detection_count": 5,
        "peak_confirmation_count": 4,
    }
    result = assess_event_risk(mock_event)
    assert result["threat_score"] == 100
    assert result["threat_level"] == "CRITICAL"
    breakdown = {item["factor"]: item["status"] for item in result["factor_breakdown"]}
    assert breakdown["Close proximity"] == "detected"
    assert breakdown["Rapid approach"] == "detected"


if __name__ == "__main__":
    test_assess_risk()
    test_explainable_risk_breakdown_collision()
    test_explainable_risk_breakdown_nominal()
    test_assess_event_risk()
    print("\nAll explainable risk-engine tests passed!")