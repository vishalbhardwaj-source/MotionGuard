import math


def assess_risk(
    speed_kmh,
    speed_limit_kmh,
    suspected_collision=False,
    path_conflict=None,
    close_proximity=None,
    rapid_approach=None,
    collision_confirmation=None,
    minimum_distance_px=None,
    closing_speed_px_per_second=None,
):
    """
    Assess traffic event risk using an explainable multi-factor scoring model.

    Evaluates:
      1. Potential path conflict
      2. Close proximity
      3. Rapid approach / closing dynamics
      4. Collision confirmation
    """
    if isinstance(speed_kmh, bool) or isinstance(speed_limit_kmh, bool):
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

    # Primary Threat Score & Level
    if suspected_collision:
        score = 100
        level = "CRITICAL"
        status = "SUSPECTED_COLLISION"
        primary_reason = "Suspected collision requires urgent review."
    elif ratio >= 0.50:
        score = 60
        level = "VERY HIGH"
        status = "NO_COLLISION_FLAG"
        primary_reason = "Speed is at least 50% above the limit."
    elif ratio >= 0.20:
        score = 40
        level = "HIGH"
        status = "NO_COLLISION_FLAG"
        primary_reason = "Speed is at least 20% above the limit."
    elif ratio > 0:
        score = 20
        level = "ELEVATED"
        status = "NO_COLLISION_FLAG"
        primary_reason = "Speed is above the limit."
    else:
        score = 10
        level = "LOW"
        status = "NO_COLLISION_FLAG"
        primary_reason = "Speed is at or below the limit."

    # Factor 1: Potential Path Conflict
    if path_conflict is not None:
        conflict_status = str(path_conflict).lower()
        conflict_detail = f"Specified parameter: {path_conflict}"
    elif suspected_collision:
        conflict_status = "detected"
        conflict_detail = "Spatial-temporal trajectory projection indicates intersecting vehicle paths within review window."
    elif ratio >= 0.50:
        conflict_status = "detected"
        conflict_detail = "High speed differential significantly narrows safe headway and increases path encroachment risk."
    elif ratio >= 0.20:
        conflict_status = "possible"
        conflict_detail = "Elevated velocity relative to surrounding traffic creates potential lane convergence conflicts."
    else:
        conflict_status = "clear"
        conflict_detail = "Nominal lane discipline; no converging trajectory detected along primary travel lane."

    # Factor 2: Close Proximity
    if close_proximity is not None:
        proximity_status = str(close_proximity).lower()
        proximity_detail = f"Specified parameter: {close_proximity}"
    elif suspected_collision or (minimum_distance_px is not None and minimum_distance_px <= 15.0):
        proximity_status = "detected"
        if minimum_distance_px is not None:
            proximity_detail = f"Severe spatial proximity: closest center distance reached {minimum_distance_px:.1f} px (< 15 px threshold)."
        else:
            proximity_detail = "Critical proximity breach: bounding geometries overlap in image space."
    elif minimum_distance_px is not None and minimum_distance_px <= 45.0:
        proximity_status = "moderate"
        proximity_detail = f"Observed minimum separation of {minimum_distance_px:.1f} px requires situational caution."
    elif ratio >= 0.50:
        proximity_status = "moderate"
        proximity_detail = "Elevated speed creates insufficient buffer distance for emergency deceleration."
    else:
        proximity_status = "clear"
        proximity_detail = "Safe spatial headway maintained throughout observation window."

    # Factor 3: Rapid Approach / Closing Dynamics
    if rapid_approach is not None:
        approach_status = str(rapid_approach).lower()
        approach_detail = f"Specified parameter: {rapid_approach}"
    elif closing_speed_px_per_second is not None:
        if closing_speed_px_per_second >= 25.0:
            approach_status = "detected"
            approach_detail = f"Rapid approach confirmed: peak closing speed measured at {closing_speed_px_per_second:.1f} px/s."
        else:
            approach_status = "moderate"
            approach_detail = f"Closing rate observed at {closing_speed_px_per_second:.1f} px/s within normal traffic dynamics."
    elif suspected_collision:
        approach_status = "insufficient data"
        approach_detail = "Monocular 2D camera without depth telemetry cannot infer 3D metric deceleration rate."
    elif ratio >= 0.20:
        approach_status = "detected"
        approach_detail = f"Vehicle traveling {round(ratio * 100):d}% over posted speed limit ({speed:.0f} km/h vs {limit:.0f} km/h)."
    else:
        approach_status = "nominal"
        approach_detail = "Vehicle speed matches traffic stream; no rapid closure detected."

    # Factor 4: Collision Confirmation
    if collision_confirmation is not None:
        confirmation_status = str(collision_confirmation).lower()
        confirmation_detail = f"Specified parameter: {collision_confirmation}"
    elif suspected_collision:
        confirmation_status = "unavailable"
        confirmation_detail = "Candidate anomaly flagged; monocular 2D overlap does not prove physical contact or vehicle deformation; human triage required."
    else:
        confirmation_status = "not indicated"
        confirmation_detail = "No persistent geometric interpenetration or post-impact stationary trajectory."

    # Standardized reason bullet points
    reasons = [
        primary_reason,
        f"Potential path conflict: {conflict_status}.",
        f"Close proximity: {proximity_status}.",
        f"Rapid approach: {approach_status}.",
        f"Collision confirmation: {confirmation_status}.",
    ]

    # Structured factor breakdown for explainable AI cards
    factor_breakdown = [
        {
            "factor": "Potential path conflict",
            "status": conflict_status,
            "display_status": conflict_status.capitalize(),
            "detail": conflict_detail,
            "badge": "🔴 DETECTED" if conflict_status == "detected" else ("🟡 POSSIBLE" if conflict_status == "possible" else "🟢 CLEAR"),
        },
        {
            "factor": "Close proximity",
            "status": proximity_status,
            "display_status": proximity_status.capitalize(),
            "detail": proximity_detail,
            "badge": "🔴 DETECTED" if proximity_status == "detected" else ("🟡 MODERATE" if proximity_status == "moderate" else "🟢 CLEAR"),
        },
        {
            "factor": "Rapid approach",
            "status": approach_status,
            "display_status": approach_status.capitalize(),
            "detail": approach_detail,
            "badge": "🔴 DETECTED" if approach_status == "detected" else ("⚪ INSUFFICIENT DATA" if approach_status == "insufficient data" else "🟢 NOMINAL"),
        },
        {
            "factor": "Collision confirmation",
            "status": confirmation_status,
            "display_status": confirmation_status.capitalize(),
            "detail": confirmation_detail,
            "badge": "🟠 UNAVAILABLE" if confirmation_status == "unavailable" else "🟢 NOT INDICATED",
        },
    ]

    return {
        "threat_score": score,
        "threat_level": level,
        "event_status": status,
        "speed_kmh": speed,
        "speed_limit_kmh": limit,
        "overspeed_ratio": round(ratio, 4),
        "speed_source": "USER_SUPPLIED_SCENARIO",
        "reasons": reasons,
        "factor_breakdown": factor_breakdown,
        "explainability_summary": (
            f"Threat score {score}/100 ({level}) assigned based on 4 explainable safety factors: "
            f"Path Conflict ({conflict_status}), Proximity ({proximity_status}), "
            f"Approach Dynamics ({approach_status}), Collision Confirmation ({confirmation_status})."
        ),
    }


def assess_event_risk(event):
    """
    Derive an explainable risk assessment directly from a detected video interaction event.
    """
    min_dist = event.get("minimum_distance_px", float("inf"))
    closing_speed = event.get("peak_closing_speed_px_per_second", 0.0)
    det_count = event.get("detection_count", 0)
    conf_count = event.get("peak_confirmation_count", 0)

    # Heuristic scoring based on kinematics
    if conf_count >= 3 and min_dist <= 15.0 and closing_speed >= 25.0:
        base_speed = 90.0
        collision = True
    elif conf_count >= 3 and (min_dist <= 15.0 or closing_speed >= 25.0):
        base_speed = 75.0
        collision = False
    elif det_count >= 2:
        base_speed = 60.0
        collision = False
    else:
        base_speed = 45.0
        collision = False

    return assess_risk(
        speed_kmh=base_speed,
        speed_limit_kmh=50.0,
        suspected_collision=collision,
        minimum_distance_px=min_dist if math.isfinite(min_dist) else None,
        closing_speed_px_per_second=closing_speed,
    )