import math


def assess_risk(speed_kmh, speed_limit_kmh,
                suspected_collision=False):

    if isinstance(speed_kmh, bool) or isinstance(
        speed_limit_kmh, bool
    ):
        raise ValueError("Speed inputs must be numeric.")

    try:
        speed = float(speed_kmh)
        limit = float(speed_limit_kmh)
    except (TypeError, ValueError):
        raise ValueError("Speed inputs must be numeric.")

    if not math.isfinite(speed) or not math.isfinite(limit):
        raise ValueError("Speed inputs must be finite.")

    if speed < 0 or limit <= 0:
        raise ValueError("Invalid speed or speed limit.")

    if not isinstance(suspected_collision, bool):
        raise ValueError("Collision flag must be True or False.")

    ratio = (speed - limit) / limit

    if suspected_collision:
        score = 100
        level = "CRITICAL"
        reasons = ["Suspected collision requires urgent review."]
        status = "SUSPECTED_COLLISION"

    elif ratio >= 0.50:
        score = 60
        level = "VERY HIGH"
        reasons = ["Speed is at least 50% above the limit."]
        status = "NO_COLLISION_FLAG"

    elif ratio >= 0.20:
        score = 40
        level = "HIGH"
        reasons = ["Speed is at least 20% above the limit."]
        status = "NO_COLLISION_FLAG"

    elif ratio > 0:
        score = 20
        level = "ELEVATED"
        reasons = ["Speed is above the limit."]
        status = "NO_COLLISION_FLAG"

    else:
        score = 10
        level = "LOW"
        reasons = ["Speed is at or below the limit."]
        status = "NO_COLLISION_FLAG"

    return {
        "threat_score": score,
        "threat_level": level,
        "event_status": status,
        "speed_kmh": speed,
        "speed_limit_kmh": limit,
        "overspeed_ratio": round(ratio, 4),
        "speed_source": "USER_SUPPLIED_SCENARIO",
        "reasons": reasons,
    }