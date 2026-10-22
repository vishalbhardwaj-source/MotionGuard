"""
Gemini Multimodal AI Incident Analyst & Forensic Reasoning Service for MotionGuard.

Integrates:
  - Google Gemini API (gemini-3.5-flash / gemini-3.8-flash)
  - Zero external HTTP dependencies (standard library urllib)
  - Image-space kinematic reasoning + Multimodal visual snapshot analysis
  - Built-in automatic fallback to deterministic offline forensic summaries
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Primary and fallback Gemini models
PRIMARY_MODEL = "gemini-3.5-flash"
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-flash-latest"]
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def load_env_file(dotenv_path: Optional[str] = None) -> None:
    """Zero-dependency .env loader for environment variables."""
    target_path = Path(dotenv_path) if dotenv_path else Path(__file__).resolve().parent.parent / ".env"
    if not target_path.is_file():
        # Also check current working directory
        cwd_env = Path(".env")
        if cwd_env.is_file():
            target_path = cwd_env
        else:
            return

    try:
        content = target_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val
    except Exception as exc:
        logger.debug("Could not parse .env file: %s", exc)


# Automatically attempt to load .env on import
load_env_file()


def get_gemini_api_key() -> str:
    """Retrieve Gemini API key strictly from GEMINI_API_KEY environment variable."""
    return os.environ.get("GEMINI_API_KEY", "").strip()


def test_gemini_connection(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Test connectivity and authentication with Google Gemini API."""
    import urllib.request
    import urllib.error

    key = (api_key or get_gemini_api_key()).strip()
    if not key:
        return {
            "status": "UNCONFIGURED",
            "message": "No GEMINI_API_KEY configured in environment or .env file.",
            "model": None,
        }

    for model in [PRIMARY_MODEL] + FALLBACK_MODELS:
        url = f"{GEMINI_BASE_URL}/models/{model}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [{"text": "Ping. Respond with one word: 'CONNECTED'."}]
                }
            ],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 10},
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": key,
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                return {
                    "status": "CONNECTED",
                    "model": model,
                    "message": f"Successfully connected to Google Gemini ({model}).",
                    "reply": reply,
                }
        except urllib.error.HTTPError as http_err:
            if http_err.code in (400, 401, 403):
                return {
                    "status": "AUTH_ERROR",
                    "code": http_err.code,
                    "message": f"Authentication failed: {http_err.reason}. Verify your GEMINI_API_KEY.",
                    "model": model,
                }
            continue
        except Exception as exc:
            logger.debug("Gemini connection test attempt failed for %s: %s", model, exc)
            continue

    return {
        "status": "UNAVAILABLE",
        "message": "Gemini API endpoints temporarily unavailable or timed out.",
        "model": None,
    }


def _encode_image_to_base64(image_path: str) -> Optional[Dict[str, str]]:
    """Read an image file and format it as Gemini inlineData payload."""
    path = Path(image_path)
    if not path.is_file():
        return None

    try:
        suffix = path.suffix.lower()
        mime_type = "image/jpeg"
        if suffix == ".png":
            mime_type = "image/png"
        elif suffix in (".jpg", ".jpeg"):
            mime_type = "image/jpeg"
        elif suffix == ".webp":
            mime_type = "image/webp"

        image_bytes = path.read_bytes()
        b64_data = base64.b64encode(image_bytes).decode("utf-8")
        return {
            "mime_type": mime_type,
            "data": b64_data,
        }
    except Exception as exc:
        logger.warning("Failed to encode image %s for Gemini: %s", image_path, exc)
        return None


def generate_gemini_triage_analysis(
    event: Dict[str, Any],
    risk_result: Dict[str, Any],
    image_path: Optional[str] = None,
    api_key: Optional[str] = None,
    preferred_model: str = PRIMARY_MODEL,
) -> Dict[str, Any]:
    """
    Generate an explainable AI triage analysis using Google Gemini.

    Multimodal capability: If `image_path` points to a valid evidence frame,
    Gemini visually analyzes the snapshot alongside image-space kinematics.
    """
    import urllib.request
    import urllib.error

    event_id = event.get("event_id", "EVT-UNKNOWN")
    threat_score = risk_result.get("threat_score", 0)
    threat_level = risk_result.get("threat_level", "LOW")
    dist = event.get("minimum_distance_px", "N/A")
    speed = event.get("peak_closing_speed_px_per_second", "N/A")
    obj_a = event.get("track_id_1", "Unknown")
    obj_b = event.get("track_id_2", "Unknown")
    cls_a = event.get("class_name_1", "vehicle")
    cls_b = event.get("class_name_2", "vehicle")

    dist_str = f"{dist:.2f} px" if isinstance(dist, (int, float)) else str(dist)
    speed_str = f"{speed:.2f} px/s" if isinstance(speed, (int, float)) else str(speed)

    # Deterministic fallback narrative (always available offline)
    fallback_narrative = (
        f"Forensic Assessment [{event_id}]: Critical interaction detected between {cls_a} (ID {obj_a}) "
        f"and {cls_b} (ID {obj_b}). Minimum separation: {dist_str}, Peak closing rate: {speed_str}. "
        f"Assessed threat score is {threat_score}/100 ({threat_level}). Immediate operator review advised."
    )

    key = (api_key or get_gemini_api_key()).strip()
    if not key:
        return {
            "status": "SIMULATED",
            "model": "offline-forensic-engine",
            "event_id": event_id,
            "threat_score": threat_score,
            "threat_level": threat_level,
            "summary": fallback_narrative,
            "recommended_action": "Conduct immediate CCTV operator verification before physical escalation.",
            "multimodal": False,
        }

    # Construct prompt parts
    prompt_text = (
        "You are MotionGuard's Senior Traffic Safety & Incident Forensic AI. "
        "Analyze the following traffic safety event detected by computer vision kinematics:\n"
        f"- Event ID: {event_id}\n"
        f"- Participating Track IDs: {obj_a} ({cls_a}) and {obj_b} ({cls_b})\n"
        f"- Threat Score: {threat_score}/100 ({threat_level})\n"
        f"- Minimum Center Distance: {dist_str}\n"
        f"- Peak Closing Velocity: {speed_str}\n\n"
        "Instructions:\n"
        "1. Never invent arbitrary km/h figures or road speed limits—base your analysis strictly on the image metrics and scene visual.\n"
        "2. Provide a 2-3 sentence forensic incident summary.\n"
        "3. Provide a 1-sentence recommended operational action for the dispatch center.\n"
        "4. Format your answer as concise, professional operator intelligence."
    )

    parts: list = [{"text": prompt_text}]

    image_attached = False
    if image_path:
        img_payload = _encode_image_to_base64(image_path)
        if img_payload:
            parts.insert(0, {
                "inlineData": {
                    "mimeType": img_payload["mime_type"],
                    "data": img_payload["data"],
                }
            })
            image_attached = True

    candidate_models = [preferred_model] + [m for m in FALLBACK_MODELS if m != preferred_model]

    for model in candidate_models:
        url = f"{GEMINI_BASE_URL}/models/{model}:generateContent"
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 300,
            },
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": key,
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text_response = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {
                    "status": "SUCCESS",
                    "model": model,
                    "event_id": event_id,
                    "threat_score": threat_score,
                    "threat_level": threat_level,
                    "summary": text_response,
                    "multimodal": image_attached,
                    "usage": data.get("usageMetadata", {}),
                }
        except Exception as err:
            logger.warning("Gemini model %s query failed (%s); trying fallback...", model, err)
            continue

    # All API calls failed -> return structured offline forensic summary
    return {
        "status": "FALLBACK_OFFLINE",
        "model": "deterministic-fallback",
        "event_id": event_id,
        "threat_score": threat_score,
        "threat_level": threat_level,
        "summary": fallback_narrative,
        "recommended_action": "Verify traffic camera footage manually.",
        "multimodal": False,
    }
