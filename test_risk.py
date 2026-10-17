from src.risk_engine import assess_risk

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


if __name__ == "__main__":
    test_assess_risk()
    print("\nAll risk-engine tests passed!")