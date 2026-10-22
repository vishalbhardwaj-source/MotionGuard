import math


def is_emergency_dispatch_eligible(event):
    """
    Unified canonical qualification rule for emergency responder live dispatch.
    Single source of truth used across risk engine, incident pipeline, and evaluation suite.
    
    To avoid emergency responder fatigue, live emergency dispatch requires:
      1. Physical contact overlap: peak_bbox_iou >= 0.05
      2. Multi-frame persistence: detection_count >= 2 and duration_seconds > 0.0
         - Prevents single-frame ByteTrack identity fragmentation/jitter on the same vehicle
           from triggering false alarms.
      3. Dynamic collision kinetic signature:
         - Significant closing speed prior to impact (peak_closing_speed >= 20.0 px/s), OR
         - Post-impact deceleration signature ("SUDDEN_DECELERATION" in post_impact_signals with min_dist <= 30.0)
    
    Returns:
        bool: True if event qualifies for live Priority 1 Emergency Dispatch, False if it remains in the sub-critical triage queue.
    """
    if not isinstance(event, dict):
        return False

    iou = event.get("peak_bbox_iou") or 0.0
    det_count = event.get("detection_count", 0)
    dur = event.get("duration_seconds", 0.0)
    contact_frames = event.get("contact_frame_count")
    closing = event.get("peak_closing_speed_px_per_second", 0.0)
    post_signals = event.get("post_impact_signals") or []
    min_dist = event.get("minimum_distance_px", float("inf"))

    # Must have physical overlap persisting across multiple frames (IoU >= 0.05 across >= 2 frames)
    if contact_frames is not None:
        has_multi_frame_contact = contact_frames >= 2 and iou >= 0.05
    else:
        has_multi_frame_contact = (iou >= 0.05) and (det_count >= 2 and dur > 0.0)

    # Must exhibit dynamic impact kinematics (high closing rate or post-impact halt)
    has_kinetic_impact = closing >= 20.0 or ("SUDDEN_DECELERATION" in post_signals and min_dist <= 30.0)

    return bool(has_multi_frame_contact and has_kinetic_impact)


def classify_severity(
    event_or_metrics=None,
    suspected_collision=False,
    peak_iou=0.0,
    post_impact_signals=None,
    minimum_distance_px=None,
    minimum_ttc_seconds=None,
    minimum_normalized_distance=None,
    peak_closing_speed=0.0,
    is_stopped_vehicle=False,
    stopped_duration_seconds=0.0,
    zone_type=None,
):
    """
    Classify traffic safety events into distinct operational severity categories:
      - COLLISION: Confirmed physical contact (IoU >= 0.05) or sudden kinetic halt.
      - NEAR_MISS: Critical proximity & approach dynamics without physical overlap.
      - STOPPED_VEHICLE: Stationary vehicle (velocity < 5 px/s for >= 2.0s) causing roadway obstruction.
      - NOMINAL: Routine traffic flow / standard passing.
    """
    if isinstance(event_or_metrics, dict):
        event = event_or_metrics
        suspected_collision = event.get("suspected_collision", suspected_collision)
        peak_iou = event.get("peak_bbox_iou", peak_iou) or 0.0
        post_impact_signals = event.get("post_impact_signals", post_impact_signals) or []
        minimum_distance_px = event.get("minimum_distance_px", minimum_distance_px)
        minimum_ttc_seconds = event.get("minimum_ttc_seconds", minimum_ttc_seconds)
        minimum_normalized_distance = event.get("minimum_normalized_distance", minimum_normalized_distance)
        peak_closing_speed = event.get("peak_closing_speed_px_per_second", peak_closing_speed) or 0.0
        is_stopped_vehicle = event.get("is_stopped_vehicle", is_stopped_vehicle)
        stopped_duration_seconds = event.get("stopped_duration_seconds", stopped_duration_seconds) or 0.0
        zone_type = event.get("zone_type", zone_type)

    post_impact_signals = post_impact_signals or []
    has_post_impact = bool(post_impact_signals)
    contact_overlap = peak_iou >= 0.05

    # 1. STOPPED VEHICLE CLASSIFICATION
    if is_stopped_vehicle or stopped_duration_seconds >= 2.0:
        return {
            "category": "STOPPED_VEHICLE",
            "badge": "🟠 STOPPED VEHICLE",
            "priority": 2,
            "confidence": 0.92,
            "rationale": "Stationary vehicle detected on active roadway (>2.0s cessation), creating primary collision obstacle.",
            "recommended_action": "Dispatch Highway Incident Response / Tow Patrol to secure lane and clear obstruction.",
            "dispatch_eligible": True,
            "dispatch_priority": "PRIORITY_2_HAZARD",
        }

    # 2. COLLISION CLASSIFICATION
    is_collision = (
        suspected_collision
        or (contact_overlap and (minimum_distance_px is None or minimum_distance_px <= 35.0))
        or has_post_impact
    )
    if is_collision:
        return {
            "category": "COLLISION",
            "badge": "🔴 COLLISION",
            "priority": 1,
            "confidence": 0.96 if contact_overlap else 0.88,
            "rationale": (
                "Verified physical contact overlap (IoU >= 0.05) or sudden post-impact kinetic cessation."
                if contact_overlap or has_post_impact
                else "Critical trajectory intersection with urgent operator collision flag."
            ),
            "recommended_action": "Immediate Priority 1 Authority Dispatch (EMS, Police, Fire Rescue).",
            "dispatch_eligible": True,
            "dispatch_priority": "PRIORITY_1_CRITICAL",
        }

    # 3. NEAR-MISS CLASSIFICATION
    is_imminent_ttc = minimum_ttc_seconds is not None and minimum_ttc_seconds <= 3.5
    is_critical_proximity = minimum_normalized_distance is not None and minimum_normalized_distance <= 1.8
    is_rapid_close = (
        minimum_distance_px is not None
        and minimum_distance_px <= 45.0
        and peak_closing_speed >= 15.0
    )

    if is_imminent_ttc or is_critical_proximity or is_rapid_close:
        merge_note = " in designated merge zone" if zone_type == "MERGE_ZONE" else ""
        return {
            "category": "NEAR_MISS",
            "badge": "🟡 NEAR-MISS",
            "priority": 3,
            "confidence": 0.85,
            "rationale": f"High closing dynamics / optical TTC without physical contact overlap{merge_note}.",
            "recommended_action": "Log telemetry to Near-Miss Safety Heatmap & Safety Engineering Audit.",
            "dispatch_eligible": False,
            "dispatch_priority": "MONITORING_ONLY",
        }

    # 4. NOMINAL / ROUTINE
    return {
        "category": "NOMINAL",
        "badge": "🟢 NOMINAL",
        "priority": 4,
        "confidence": 0.95,
        "rationale": "Separation distance and closure kinematics within regular traffic stream baseline.",
        "recommended_action": "Passive surveillance logging; no intervention required.",
        "dispatch_eligible": False,
        "dispatch_priority": "NONE",
    }


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
    severity_category=None,
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

    # Multi-class severity classification
    if severity_category:
        severity = classify_severity(
            suspected_collision=(severity_category == "COLLISION"),
            is_stopped_vehicle=(severity_category == "STOPPED_VEHICLE"),
            minimum_distance_px=minimum_distance_px,
            peak_closing_speed=closing_speed_px_per_second or 0.0,
        )
    else:
        severity = classify_severity(
            suspected_collision=suspected_collision,
            minimum_distance_px=minimum_distance_px,
            peak_closing_speed=closing_speed_px_per_second or 0.0,
        )

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
        "severity": severity,
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

    min_ttc = event.get("minimum_ttc_seconds")
    min_norm_dist = event.get("minimum_normalized_distance")
    peak_iou = event.get("peak_bbox_iou", 0.0) or 0.0
    signals = event.get("post_impact_signals", [])

    has_post_impact = bool(signals)
    contact_overlap = peak_iou >= 0.05
    imminent_ttc = min_ttc is not None and min_ttc < 1.5

    # Multi-class severity derivation
    severity = classify_severity(event)

    # Physics-grounded threat classification
    if severity["category"] == "COLLISION" or (contact_overlap or has_post_impact) and min_dist <= 30.0:
        base_speed = 95.0
        collision = True
    elif severity["category"] == "STOPPED_VEHICLE":
        base_speed = 80.0
        collision = False
    elif conf_count >= 3 and min_dist <= 15.0 and closing_speed >= 25.0:
        base_speed = 90.0
        collision = True
    elif imminent_ttc or (min_norm_dist is not None and min_norm_dist < 1.0):
        base_speed = 75.0
        collision = False
    elif conf_count >= 3 and (min_dist <= 25.0 or closing_speed >= 25.0):
        base_speed = 75.0
        collision = False
    elif det_count >= 2:
        base_speed = 60.0
        collision = False
    else:
        base_speed = 45.0
        collision = False

    result = assess_risk(
        speed_kmh=base_speed,
        speed_limit_kmh=50.0,
        suspected_collision=collision,
        minimum_distance_px=min_dist if math.isfinite(min_dist) else None,
        closing_speed_px_per_second=closing_speed,
    )
    result["severity"] = severity
    return result
