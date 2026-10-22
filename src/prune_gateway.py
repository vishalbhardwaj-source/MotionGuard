"""
Prune AI Gateway & Event Pruning Integration for MotionGuard.

Integrates:
  1. Prune AI Gateway (https://withprune.com):
     Unified proxy for LLM routing, telemetry caching, and incident triage summaries.
     Operates with zero external dependencies (pure Python standard library) and 
     includes a deterministic SIMULATOR mode requiring zero API keys or credentials.
  2. Interaction Event Pruning:
     Prunes benign, nominal, or sub-threshold interaction events to eliminate
     jitter and optimize forensic dispatch triage.
"""

import os
import json
import logging
from pathlib import Path
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def _load_env_file():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        env_path = Path(".env")
    if env_path.is_file():
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
        except Exception:
            pass


_load_env_file()

# Prune Gateway Configuration
PRUNE_GATEWAY_URL = os.environ.get("PRUNE_BASE_URL", "https://api.withprune.com/v1")
PRUNE_API_KEY = os.environ.get("PRUNE_API_KEY", "")


def prune_nominal_candidates(
    events: List[Dict[str, Any]],
    min_threat_score: float = 25.0,
    risk_scorer=None,
) -> List[Dict[str, Any]]:
    """
    Intelligent candidate event pruning.
    Prunes low-threat background jitter and nominal passing events from the candidate queue.
    
    Args:
        events: List of interaction events.
        min_threat_score: Minimum threat score threshold to retain an event (default 25.0).
        risk_scorer: Scorer callable, defaults to assess_event_risk from src.risk_engine.
        
    Returns:
        List of candidate events whose threat score meets or exceeds min_threat_score.
    """
    if not events:
        return []

    if risk_scorer is None:
        from src.risk_engine import assess_event_risk
        risk_scorer = assess_event_risk

    filtered_events = []
    for ev in events:
        try:
            risk = risk_scorer(ev)
            score = risk.get("threat_score", 0)
            if score >= min_threat_score:
                ev_copy = dict(ev)
                ev_copy["prune_filtered"] = False
                ev_copy["prune_assessed_score"] = score
                filtered_events.append(ev_copy)
        except Exception as err:
            logger.debug("Pruning evaluation error for event %s: %s", ev.get("event_id"), err)
            # Retain on error to prevent dropping critical candidates
            filtered_events.append(ev)

    return filtered_events


def generate_prune_triage_summary(
    event: Dict[str, Any],
    risk_result: Dict[str, Any],
    model: str = "prune-router-fast",
    gateway_mode: str = "AUTO",
) -> Dict[str, Any]:
    """
    Generate an explainable incident triage summary using the Prune AI Gateway.
    
    When in SIMULATOR mode or when no PRUNE_API_KEY is configured, returns a deterministic,
    offline forensic summary in pixels and px/s (zero credentials required).
    When PRUNE_API_KEY is set and gateway_mode != 'SIMULATOR', routes the prompt through Prune.
    
    Args:
        event: Interaction event dictionary.
        risk_result: Output from assess_event_risk.
        model: Model routing identifier configured in Prune dashboard.
        gateway_mode: 'AUTO', 'SIMULATOR', or 'LIVE'.
        
    Returns:
        dict: Triage summary report with status, narrative, and gateway metadata.
    """
    event_id = event.get("event_id", "EVT-UNKNOWN")
    score = risk_result.get("threat_score", 0)
    level = risk_result.get("threat_level", "LOW")
    dist = event.get("minimum_distance_px", "N/A")
    speed = event.get("peak_closing_speed_px_per_second", "N/A")

    # Format deterministic forensic summary (always pixel-based, zero invented speeds)
    dist_str = f"{dist:.2f} px" if isinstance(dist, (int, float)) else str(dist)
    speed_str = f"{speed:.2f} px/s" if isinstance(speed, (int, float)) else str(speed)

    fallback_narrative = (
        f"MotionGuard Candidate Incident [{event_id}]: "
        f"Assessed threat level {level} (Score {score}/100) based on image-space kinematics. "
        f"Measured minimum separation of {dist_str} and peak closing rate of {speed_str}. "
        f"Human review recommended prior to emergency escalation."
    )

    api_key = os.environ.get("PRUNE_API_KEY", PRUNE_API_KEY).strip()
    use_live = (gateway_mode == "LIVE" or (gateway_mode == "AUTO" and bool(api_key)))

    if not use_live or not api_key:
        return {
            "status": "SIMULATED",
            "gateway": "PRUNE_SIMULATOR",
            "model": model,
            "event_id": event_id,
            "threat_score": score,
            "threat_level": level,
            "triage_summary": fallback_narrative,
            "receipt": {
                "tokens_cached": 0,
                "latency_ms": 1.2,
                "prune_shield_status": "PASS",
            },
        }

    # Live Prune Gateway call
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a forensic traffic safety triage assistant. "
                    "Explain video events using ONLY image-space metrics (pixels and px/s). "
                    "Never invent km/h figures, speed limits, or confirm collisions without human review."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate a concise 2-sentence operator triage note for Event {event_id}. "
                    f"Threat level: {level} ({score}/100). Minimum separation: {dist_str}. "
                    f"Peak closing speed: {speed_str}."
                ),
            },
        ],
        "max_tokens": 120,
        "temperature": 0.2,
    }

    req = urllib.request.Request(
        f"{PRUNE_GATEWAY_URL.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "MotionGuard-Prune-Integration/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"].strip()
            return {
                "status": "SUCCESS",
                "gateway": "PRUNE_LIVE_GATEWAY",
                "model": data.get("model", model),
                "event_id": event_id,
                "threat_score": score,
                "threat_level": level,
                "triage_summary": content,
                "receipt": data.get("usage", {}),
            }
    except Exception as err:
        logger.warning("Prune live gateway call failed (%s); reverting to deterministic summary.", err)
        return {
            "status": "FALLBACK_SIMULATED",
            "gateway": "PRUNE_SIMULATOR",
            "model": model,
            "event_id": event_id,
            "threat_score": score,
            "threat_level": level,
            "triage_summary": fallback_narrative,
            "error": str(err),
        }
