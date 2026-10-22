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

    # Safe float parsing to prevent TypeError during numeric comparisons
    if minimum_distance_px is not None:
        try:
            minimum_distance_px = float(minimum_distance_px)
        except (ValueError, TypeError):
            minimum_distance_px = None
    if peak_closing_speed is not None:
        try:
            peak_closing_speed = float(peak_closing_speed)
        except (ValueError, TypeError):
            peak_closing_speed = 0.0

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


# ==============================================================================
# Centralized Image-Space Risk Scorer Configuration
# ==============================================================================
IMAGE_SPACE_RISK_THRESHOLDS = {
    # Continuous scoring bands (pixels and px/s)
    "distance_band_min_px": 12.0,      # Distance at or below which maximum distance points are awarded
    "distance_band_max_px": 100.0,     # Distance at or above which 0 distance points are awarded
    "speed_band_max_px_s": 50.0,       # Closing speed at or above which maximum speed points are awarded

    # Scoring weights (sum to 100.0)
    "weight_distance": 50.0,           # Max points for close proximity
    "weight_closing_speed": 35.0,      # Max points for rapid approach
    "weight_persistence": 15.0,        # Max points for multi-frame persistence

    # Persistence & confirmation point tiers
    "persistence_tier_critical_pts": 15.0,
    "persistence_tier_high_pts": 12.0,
    "persistence_tier_medium_pts": 8.0,
    "persistence_tier_low_pts": 4.0,

    # Threat level score cutoffs
    "cutoff_critical": 85,
    "cutoff_very_high": 65,
    "cutoff_high": 45,
    "cutoff_elevated": 25,

    # Factor card thresholds (for qualitative explainability badges)
    "distance_critical_px": 15.0,
    "distance_moderate_px": 45.0,
    "closing_speed_critical_px_s": 30.0,
    "closing_speed_moderate_px_s": 15.0,
    "confirmation_count_critical": 4,
}
EVENT_RISK_THRESHOLDS = IMAGE_SPACE_RISK_THRESHOLDS


def _build_insufficient_data_risk(event=None):
    """Fallback risk report when event lacks distance telemetry (Edge case)."""
    event = event or {}
    severity = classify_severity(event)
    crit_dist = IMAGE_SPACE_RISK_THRESHOLDS["distance_critical_px"]
    mod_dist = IMAGE_SPACE_RISK_THRESHOLDS["distance_moderate_px"]
    crit_speed = IMAGE_SPACE_RISK_THRESHOLDS["closing_speed_critical_px_s"]

    factor_breakdown = [
        {
            "factor": "Potential path conflict",
            "status": "clear",
            "display_status": "Clear",
            "detail": "Insufficient trajectory distance data to assess convergence path.",
            "badge": "🟢 CLEAR",
        },
        {
            "factor": "Close proximity",
            "status": "insufficient data",
            "display_status": "Insufficient Data",
            "detail": f"Measured separation: N/A (threshold: <= {crit_dist:.1f} px for detected, <= {mod_dist:.1f} px for moderate).",
            "badge": "⚪ INSUFFICIENT DATA",
        },
        {
            "factor": "Rapid approach",
            "status": "insufficient data",
            "display_status": "Insufficient Data",
            "detail": f"Measured closing speed: N/A (threshold: >= {crit_speed:.1f} px/s for detected).",
            "badge": "⚪ INSUFFICIENT DATA",
        },
        {
            "factor": "Collision confirmation",
            "status": "not indicated",
            "display_status": "Not Indicated",
            "detail": "No physical contact overlap or post-impact kinetic cessation detected.",
            "badge": "🟢 NOT INDICATED",
        },
    ]

    reasons = [
        "Image-space kinematic threat assessed at LOW (10/100).",
        "Potential path conflict: clear.",
        "Close proximity: insufficient data.",
        "Rapid approach: insufficient data.",
        "Collision confirmation: not indicated.",
    ]

    return {
        "threat_score": 10,
        "threat_level": "LOW",
        "event_status": "LOW_THREAT_INTERACTION",
        "severity": severity,
        "speed_kmh": None,
        "speed_limit_kmh": None,
        "overspeed_ratio": None,
        "speed_source": "IMAGE_SPACE_VIDEO_EVENT",
        "reasons": reasons,
        "factor_breakdown": factor_breakdown,
        "explainability_summary": (
            f"Threat score 10/100 (LOW) assigned based on image-space pixel metrics: "
            f"event lacks sufficient tracking distance data."
        ),
        "thresholds_used": dict(IMAGE_SPACE_RISK_THRESHOLDS),
    }


def assess_event_risk(event):
    """
    Derive an explainable risk assessment directly from a detected video interaction event.
    Evaluates risk purely in image space (pixels and pixels per second) with no invented speeds.
    """
    if event is None or not isinstance(event, dict) or not event:
        return _build_insufficient_data_risk()

    if "minimum_distance_px" not in event or event.get("minimum_distance_px") is None:
        return _build_insufficient_data_risk(event)

    raw_dist = event.get("minimum_distance_px")
    raw_closing = event.get("peak_closing_speed_px_per_second", 0.0)

    # 1. Input validation in the style of assess_risk:
    # Reject strings (e.g. "12") and booleans (isinstance(True, int) is True in Python)
    if isinstance(raw_dist, (str, bool)):
        raise ValueError("Distance must be numeric, not string or boolean.")
    if isinstance(raw_closing, (str, bool)):
        raise ValueError("Closing speed must be numeric, not string or boolean.")

    try:
        dist = float(raw_dist)
        closing = float(raw_closing) if raw_closing is not None else 0.0
    except (TypeError, ValueError):
        raise ValueError("Distance and closing speed must be numeric.")

    if not math.isfinite(dist) or not math.isfinite(closing):
        raise ValueError("Distance and closing speed must be finite.")

    if dist < 0 or closing < 0:
        raise ValueError("Distance and closing speed cannot be negative.")

    det_count = int(event.get("detection_count") or 0)
    conf_count = int(event.get("peak_confirmation_count") or 0)

    # 2. Monotonic composite image-space scoring derived strictly from constants
    d_min = IMAGE_SPACE_RISK_THRESHOLDS["distance_band_min_px"]
    d_max = IMAGE_SPACE_RISK_THRESHOLDS["distance_band_max_px"]
    w_dist = IMAGE_SPACE_RISK_THRESHOLDS["weight_distance"]
    w_speed = IMAGE_SPACE_RISK_THRESHOLDS["weight_closing_speed"]
    s_max = IMAGE_SPACE_RISK_THRESHOLDS["speed_band_max_px_s"]

    # Distance component (0 to w_dist pts): smaller distance -> higher score
    if dist <= d_min:
        s_dist = w_dist
    elif dist >= d_max:
        s_dist = 0.0
    else:
        s_dist = w_dist * (1.0 - (dist - d_min) / (d_max - d_min))

    # Closing speed component (0 to w_speed pts): higher speed -> higher score
    if closing >= s_max:
        s_speed = w_speed
    elif closing <= 0.0:
        s_speed = 0.0
    else:
        s_speed = w_speed * (closing / s_max)

    # Persistence & confirmation component (0 to weight_persistence pts)
    p_crit = IMAGE_SPACE_RISK_THRESHOLDS["persistence_tier_critical_pts"]
    p_high = IMAGE_SPACE_RISK_THRESHOLDS["persistence_tier_high_pts"]
    p_med = IMAGE_SPACE_RISK_THRESHOLDS["persistence_tier_medium_pts"]
    p_low = IMAGE_SPACE_RISK_THRESHOLDS["persistence_tier_low_pts"]

    if det_count >= 5 and conf_count >= 4:
        s_conf = p_crit
    elif det_count >= 3 and conf_count >= 3:
        s_conf = p_high
    elif det_count >= 2 or conf_count >= 2:
        s_conf = p_med
    elif det_count >= 1 or conf_count >= 1:
        s_conf = p_low
    else:
        s_conf = 0.0

    raw_score = s_dist + s_speed + s_conf

    # Score comes strictly from pixel metrics — no artificial score floor!
    score = int(min(100, max(0, round(raw_score))))

    # Multi-class severity classification derivation (for taxonomy only, sanitized against strings)
    sanitized_event = dict(event)
    sanitized_event["minimum_distance_px"] = dist
    sanitized_event["peak_closing_speed_px_per_second"] = closing
    severity = classify_severity(sanitized_event)

    # Threat level mapping derived from centralized cutoffs
    cut_crit = IMAGE_SPACE_RISK_THRESHOLDS["cutoff_critical"]
    cut_vh = IMAGE_SPACE_RISK_THRESHOLDS["cutoff_very_high"]
    cut_high = IMAGE_SPACE_RISK_THRESHOLDS["cutoff_high"]
    cut_elev = IMAGE_SPACE_RISK_THRESHOLDS["cutoff_elevated"]

    if score >= cut_crit:
        level = "CRITICAL"
    elif score >= cut_vh:
        level = "VERY HIGH"
    elif score >= cut_high:
        level = "HIGH"
    elif score >= cut_elev:
        level = "ELEVATED"
    else:
        level = "LOW"

    status = f"{level}_IMAGE_SPACE_INTERACTION"

    # 3. Factor status derivation & transparent threshold comparison
    crit_dist = IMAGE_SPACE_RISK_THRESHOLDS["distance_critical_px"]
    mod_dist = IMAGE_SPACE_RISK_THRESHOLDS["distance_moderate_px"]
    crit_speed = IMAGE_SPACE_RISK_THRESHOLDS["closing_speed_critical_px_s"]
    mod_speed = IMAGE_SPACE_RISK_THRESHOLDS["closing_speed_moderate_px_s"]
    crit_conf = IMAGE_SPACE_RISK_THRESHOLDS["confirmation_count_critical"]

    # Factor: Close proximity
    if dist <= crit_dist:
        proximity_status = "detected"
        proximity_badge = "🔴 DETECTED"
    elif dist <= mod_dist:
        proximity_status = "moderate"
        proximity_badge = "🟡 MODERATE"
    else:
        proximity_status = "clear"
        proximity_badge = "🟢 CLEAR"
    proximity_detail = (
        f"Measured separation: {dist:.2f} px (threshold: <= {crit_dist:.1f} px for detected, "
        f"<= {mod_dist:.1f} px for moderate)."
    )

    # Factor: Rapid approach
    if closing >= crit_speed:
        approach_status = "detected"
        approach_badge = "🔴 DETECTED"
    elif closing >= mod_speed:
        approach_status = "moderate"
        approach_badge = "🟡 MODERATE"
    else:
        approach_status = "nominal"
        approach_badge = "🟢 NOMINAL"
    approach_detail = (
        f"Measured closing speed: {closing:.2f} px/s (threshold: >= {crit_speed:.1f} px/s for detected, "
        f">= {mod_speed:.1f} px/s for moderate)."
    )

    # Factor: Potential path conflict
    if dist <= crit_dist and closing >= mod_speed:
        conflict_status = "detected"
        conflict_badge = "🔴 DETECTED"
        conflict_detail = (
            f"Converging trajectory dynamics: measured distance {dist:.2f} px (threshold <= {crit_dist:.1f} px) "
            f"with closing rate {closing:.2f} px/s (threshold >= {mod_speed:.1f} px/s)."
        )
    elif dist <= mod_dist or closing >= mod_speed:
        conflict_status = "possible"
        conflict_badge = "🟡 POSSIBLE"
        conflict_detail = (
            f"Intersecting approach vectors: measured distance {dist:.2f} px (threshold <= {mod_dist:.1f} px), "
            f"closing rate {closing:.2f} px/s (threshold >= {mod_speed:.1f} px/s)."
        )
    else:
        conflict_status = "clear"
        conflict_badge = "🟢 CLEAR"
        conflict_detail = (
            f"Nominal separation dynamics: measured distance {dist:.2f} px and closing rate {closing:.2f} px/s "
            f"within safe baselines."
        )

    # Factor: Collision confirmation
    peak_iou = event.get("peak_bbox_iou") or 0.0
    signals = event.get("post_impact_signals") or []
    has_contact = (peak_iou >= 0.05) or bool(signals) or (conf_count >= 3 and dist <= 15.0 and closing >= 25.0)
    if has_contact:
        confirmation_status = "detected"
        confirmation_badge = "🔴 DETECTED"
        confirmation_detail = (
            f"Multi-frame confirmation detected: {conf_count} confirmed frames with measured separation {dist:.2f} px "
            f"(threshold <= {crit_dist:.1f} px)."
        )
    else:
        confirmation_status = "not indicated"
        confirmation_badge = "🟢 NOT INDICATED"
        confirmation_detail = (
            f"Multi-frame confirmation: {conf_count} frames recorded "
            f"(threshold: >= {crit_conf} frames for critical persistence)."
        )

    # 4. Structured factor cards
    factor_breakdown = [
        {
            "factor": "Potential path conflict",
            "status": conflict_status,
            "display_status": conflict_status.capitalize(),
            "detail": conflict_detail,
            "badge": conflict_badge,
            "measured_value": f"{dist:.2f} px, {closing:.2f} px/s",
            "threshold": f"<={crit_dist:.1f} px, >={mod_speed:.1f} px/s",
        },
        {
            "factor": "Close proximity",
            "status": proximity_status,
            "display_status": proximity_status.capitalize(),
            "detail": proximity_detail,
            "badge": proximity_badge,
            "measured_value": f"{dist:.2f} px",
            "threshold": f"<={crit_dist:.1f} px",
        },
        {
            "factor": "Rapid approach",
            "status": approach_status,
            "display_status": approach_status.capitalize(),
            "detail": approach_detail,
            "badge": approach_badge,
            "measured_value": f"{closing:.2f} px/s",
            "threshold": f">={crit_speed:.1f} px/s",
        },
        {
            "factor": "Collision confirmation",
            "status": confirmation_status,
            "display_status": confirmation_status.capitalize(),
            "detail": confirmation_detail,
            "badge": confirmation_badge,
            "measured_value": f"{conf_count} frames",
            "threshold": f">={crit_conf} frames",
        },
    ]

    reasons = [
        f"Image-space kinematic threat assessed at {level} ({score}/100).",
        f"Potential path conflict: {conflict_status}.",
        f"Close proximity: {proximity_status}.",
        f"Rapid approach: {approach_status}.",
        f"Collision confirmation: {confirmation_status}.",
    ]

    explainability_summary = (
        f"Threat score {score}/100 ({level}) derived from image-space pixel kinematics: "
        f"measured separation {dist:.2f} px vs {crit_dist:.1f} px threshold, "
        f"closing speed {closing:.2f} px/s vs {crit_speed:.1f} px/s threshold, "
        f"and {conf_count} persistent confirmation frames."
    )

    return {
        "threat_score": score,
        "threat_level": level,
        "event_status": status,
        "severity": severity,
        "speed_kmh": None,
        "speed_limit_kmh": None,
        "overspeed_ratio": None,
        "speed_source": "IMAGE_SPACE_VIDEO_EVENT",
        "reasons": reasons,
        "factor_breakdown": factor_breakdown,
        "explainability_summary": explainability_summary,
        "thresholds_used": dict(IMAGE_SPACE_RISK_THRESHOLDS),
    }
