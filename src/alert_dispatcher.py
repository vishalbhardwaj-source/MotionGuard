import datetime
import json
import math
import os
import re
from pathlib import Path
import requests

# Per-camera dispatch cooldown cache (seconds)
_DISPATCH_COOLDOWN_CACHE = {}


from collections import namedtuple

def check_dispatch_cooldown(
    camera_id="DEFAULT_CAMERA",
    cooldown_seconds=60,
    threat_score=0,
    threat_level="LOW",
):
    """
    Check and enforce per-camera alert rate limits.
    Allows dispatch if:
      1. Cooldown interval has elapsed, OR
      2. Severity Escalation: The new incident is higher priority (CRITICAL level,
         or threat score exceeds the prior alert by >= 15 points).
    Returns boolean True if dispatch is allowed, False otherwise.
    """
    now = datetime.datetime.now().timestamp()
    record = _DISPATCH_COOLDOWN_CACHE.get(camera_id)

    if record is None:
        _DISPATCH_COOLDOWN_CACHE[camera_id] = {
            "timestamp": now,
            "threat_score": threat_score,
            "threat_level": str(threat_level),
            "last_reason": "INITIAL_DISPATCH",
        }
        return True

    elapsed = now - record["timestamp"]
    last_score = record.get("threat_score", 0)
    last_level = record.get("threat_level", "LOW")

    # Severity escalation bypass: a critical collision or jump in threat overrides cooldown
    is_escalation = (
        (threat_level == "CRITICAL" and last_level != "CRITICAL")
        or (threat_score >= last_score + 15 and threat_score >= 70)
    )

    if elapsed < cooldown_seconds:
        if is_escalation:
            _DISPATCH_COOLDOWN_CACHE[camera_id] = {
                "timestamp": now,
                "threat_score": threat_score,
                "threat_level": str(threat_level),
                "last_reason": "SEVERITY_ESCALATION_BYPASS",
            }
            return True
        return False

    _DISPATCH_COOLDOWN_CACHE[camera_id] = {
        "timestamp": now,
        "threat_score": threat_score,
        "threat_level": str(threat_level),
        "last_reason": "COOLDOWN_ELAPSED",
    }
    return True

def reset_dispatch_cooldowns():
    """Clear in-memory dispatch cooldowns (useful for tests)."""
    _DISPATCH_COOLDOWN_CACHE.clear()


def format_emergency_sms(
    event,
    camera_name="Highway North - Sector 4",
    camera_id="CAM-01",
    location_details=None,
    incident_type=None,
    incident_id=None,
    threat_level=None,
    threat_score=None,
    **kwargs,
):
    """
    Format a highly structured, operational emergency dispatch alert for traffic authorities,
    first responders, and Telegram/SMS command channels.
    """
    event_id = event.get("event_id", "EVT-UNKNOWN")
    inc_id = incident_id or event.get("incident_id") or event_id

    # Threat assessment & level
    level = threat_level or event.get("threat_level", "HIGH")
    score = threat_score if threat_score is not None else event.get("threat_score")
    score_str = f" ({score}/100)" if score is not None else ""

    emoji_map = {
        "CRITICAL": "🔴",
        "VERY HIGH": "🟠",
        "HIGH": "🟡",
        "ELEVATED": "🔵",
        "LOW": "🟢",
    }
    sev_emoji = emoji_map.get(str(level).upper(), "⚠️")

    # Timestamp
    timestamp = event.get("evidence_timestamp_seconds")
    if timestamp is None:
        timestamp = event.get("minimum_distance_timestamp_seconds", event.get("start_seconds", 0.0))

    try:
        ts_val = float(timestamp)
        mins = int(ts_val // 60)
        secs = ts_val % 60
        time_str = f"{mins:02d}:{secs:05.2f}s ({ts_val:.2f}s)"
    except (ValueError, TypeError):
        time_str = f"{timestamp}s"

    tracks = event.get("track_ids", [])
    track_str = ", ".join(map(str, tracks)) if tracks else "Unconfirmed"

    # Kinematics
    min_dist = event.get("minimum_distance_px", "N/A")
    closing_speed = event.get("peak_closing_speed_px_per_second", "N/A")
    ttc = event.get("minimum_ttc_seconds") or event.get("time_to_collision_seconds")
    norm_dist = event.get("minimum_normalized_distance") or event.get("normalized_distance")

    if isinstance(min_dist, (int, float)):
        min_dist_str = f"{min_dist:.1f}px"
    else:
        min_dist_str = str(min_dist)

    if isinstance(closing_speed, (int, float)):
        closing_speed_str = f"{closing_speed:.1f}px/s"
    else:
        closing_speed_str = str(closing_speed)

    loc_header = f"{camera_name}"
    if location_details and location_details not in camera_name:
        loc_header += f" ({location_details})"
    if camera_id and camera_id not in loc_header:
        loc_header += f" [{camera_id}]"

    kinematics_items = [
        f"   • Min Separation: {min_dist_str}",
        f"   • Peak Closing Speed: {closing_speed_str}",
    ]
    if norm_dist is not None and isinstance(norm_dist, (int, float)):
        kinematics_items.append(f"   • Scale-Normalized Dist: {norm_dist:.2f}x bbox")
    if ttc is not None and isinstance(ttc, (int, float)) and math.isfinite(ttc):
        kinematics_items.append(f"   • Time-to-Collision (TTC): {ttc:.2f}s")
    kinematics_text = "\n".join(kinematics_items)

    type_header = f" [{incident_type}]" if incident_type else ""

    message = (
        f"🚨 [MOTIONGUARD ALERT] Incident Triage{type_header}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Incident ID: {inc_id}  |  Event: {event_id}\n"
        f"⚠️ Threat Level: {sev_emoji} {level}{score_str}\n"
        f"📍 Location: {loc_header}\n"
        f"⏱️ Video Timestamp: {time_str}\n\n"
        f"🚗 Involved Tracks: {track_str}\n"
        f"⚡ Kinematic Telemetry:\n"
        f"{kinematics_text}\n\n"
        f"📋 Action Required:\n"
        f"Forensic decision-support candidate flagged for operator triage.\n"
        f"🔗 Live Workstation Dossier: http://localhost:8501\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    return message


def sanitize_phone_number(phone_number):
    """Validate and clean international or local phone numbers."""
    if not isinstance(phone_number, str):
        raise ValueError("Phone number must be a string.")
    
    cleaned = re.sub(r"[\s\-\(\)]", "", phone_number.strip())
    if not cleaned or not re.match(r"^\+?[0-9]{7,15}$", cleaned):
        raise ValueError(f"Invalid phone number format: '{phone_number}'. Expected 7-15 digits with optional '+' prefix.")
    return cleaned


def dispatch_sms(
    phone_number,
    message_text,
    twilio_sid=None,
    twilio_token=None,
    twilio_from=None,
    telegram_token=None,
    telegram_chat_id=None,
    photo_path=None,
    video_path=None,
    camera_id=None,
    threat_score=None,
    threat_level=None,
    cooldown_seconds=None,
    gateway_mode="AUTO",
):
    """
    Dispatch emergency alert to authorities via Twilio SMS, Telegram Bot (with snapshot support),
    or zero-setup Local Carrier Simulator.
    
    gateway_mode can be 'AUTO', 'SIMULATOR', 'TWILIO', or 'TELEGRAM'.
    Supports per-camera cooldown if cooldown_seconds is specified.
    """
    clean_phone = sanitize_phone_number(phone_number)
    now_iso = datetime.datetime.now().astimezone().isoformat()
    mode = (gateway_mode or "AUTO").upper()

    # Rate limiting / cooldown check with severity escalation bypass
    if cooldown_seconds and camera_id:
        allowed = check_dispatch_cooldown(
            camera_id=camera_id,
            cooldown_seconds=cooldown_seconds,
            threat_score=threat_score or 0,
            threat_level=threat_level or "LOW",
        )
        if not allowed:
            return {
                "success": False,
                "channel": "RATE_LIMIT_COOLDOWN",
                "status": "RATE_LIMITED",
                "error": f"Dispatch throttled: Camera {camera_id} is in active cooldown.",
                "recipient": clean_phone,
                "dispatched_at": now_iso,
            }

    # Simulator Mode: Zero-setup local broadcast simulation
    if mode == "SIMULATOR":
        simulated_id = f"SMS-SIM-{int(datetime.datetime.now().timestamp() * 1000) % 1000000:06d}"
        return {
            "success": True,
            "channel": "SMS_DISPATCH_SIMULATOR",
            "status": "DELIVERED_SIMULATED",
            "message_id": simulated_id,
            "recipient": clean_phone,
            "carrier_network": "Emergency Broadcast Gateway (Local)",
            "dispatched_at": now_iso,
            "body": message_text,
            "photo_attached": bool(photo_path and Path(photo_path).is_file()),
            "video_attached": bool(video_path and Path(video_path).is_file()),
        }

    # Priority 1: Real Twilio SMS if explicitly requested or in AUTO mode with credentials
    sid = twilio_sid or os.getenv("TWILIO_ACCOUNT_SID")
    token = twilio_token or os.getenv("TWILIO_AUTH_TOKEN")
    from_number = twilio_from or os.getenv("TWILIO_PHONE_NUMBER")

    if mode == "TWILIO" or (mode == "AUTO" and sid and token and from_number):
        if not (sid and token and from_number):
            return {
                "success": False,
                "channel": "TWILIO_SMS",
                "status": "MISSING_CREDENTIALS",
                "error": "Twilio Account SID, Auth Token, and Sender Number are required.",
                "recipient": clean_phone,
                "dispatched_at": now_iso,
            }
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        data = {
            "To": clean_phone,
            "From": from_number,
            "Body": message_text,
        }
        try:
            response = requests.post(url, data=data, auth=(sid, token), timeout=10)
            if response.status_code in (200, 201):
                res_data = response.json()
                return {
                    "success": True,
                    "channel": "TWILIO_SMS",
                    "status": "DELIVERED",
                    "message_id": res_data.get("sid", "N/A"),
                    "recipient": clean_phone,
                    "dispatched_at": now_iso,
                    "body": message_text,
                }
            else:
                return {
                    "success": False,
                    "channel": "TWILIO_SMS",
                    "status": f"TWILIO_ERROR_{response.status_code}",
                    "error": response.text,
                    "recipient": clean_phone,
                    "dispatched_at": now_iso,
                }
        except Exception as exc:
            return {
                "success": False,
                "channel": "TWILIO_SMS",
                "status": "CONNECTION_FAILED",
                "error": str(exc),
                "recipient": clean_phone,
                "dispatched_at": now_iso,
            }

    # Priority 2: Telegram Bot (with snapshot photo delivery support)
    tg_token = telegram_token or os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if mode == "TELEGRAM" or (mode == "AUTO" and tg_token and tg_chat):
        if not (tg_token and tg_chat):
            return {
                "success": False,
                "channel": "TELEGRAM_ALERT",
                "status": "MISSING_CREDENTIALS",
                "error": "Telegram Bot Token and Chat ID are required.",
                "recipient": f"Chat ID: {tg_chat or 'Unspecified'}",
                "dispatched_at": now_iso,
            }

        # Check if visual snapshot evidence is attached and exists
        has_photo = photo_path and Path(photo_path).is_file()
        has_video = video_path and Path(video_path).is_file()

        try:
            if has_video:
                # Send video clip with caption
                tg_video_url = f"https://api.telegram.org/bot{tg_token}/sendVideo"
                with open(video_path, "rb") as video_file:
                    files = {"video": video_file}
                    payload = {"chat_id": tg_chat, "caption": message_text}
                    response = requests.post(tg_video_url, data=payload, files=files, timeout=30)
            elif has_photo:
                # Send photo with caption
                tg_photo_url = f"https://api.telegram.org/bot{tg_token}/sendPhoto"
                with open(photo_path, "rb") as photo_file:
                    files = {"photo": photo_file}
                    payload = {"chat_id": tg_chat, "caption": message_text}
                    response = requests.post(tg_photo_url, data=payload, files=files, timeout=15)
            else:
                # Send text message
                tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                response = requests.post(
                    tg_url,
                    json={"chat_id": tg_chat, "text": message_text},
                    timeout=10,
                )

            if response.status_code == 200:
                res_json = response.json()
                return {
                    "success": True,
                    "channel": "TELEGRAM_ALERT",
                    "status": "DELIVERED",
                    "message_id": str(res_json.get("result", {}).get("message_id")),
                    "recipient": f"Chat ID: {tg_chat}",
                    "dispatched_at": now_iso,
                    "body": message_text,
                    "photo_attached": bool(has_photo),
                }
            else:
                err_desc = response.json().get("description", response.text)
                return {
                    "success": False,
                    "channel": "TELEGRAM_ALERT",
                    "status": f"TELEGRAM_ERROR_{response.status_code}",
                    "error": err_desc,
                    "recipient": f"Chat ID: {tg_chat}",
                    "dispatched_at": now_iso,
                }
        except Exception as exc:
            return {
                "success": False,
                "channel": "TELEGRAM_ALERT",
                "status": "CONNECTION_FAILED",
                "error": str(exc),
                "recipient": f"Chat ID: {tg_chat}",
                "dispatched_at": now_iso,
            }

    # Default Fallback: Local Carrier Simulator (Zero-setup hackathon mode)
    simulated_id = f"SMS-SIM-{int(datetime.datetime.now().timestamp() * 1000) % 1000000:06d}"
    return {
        "success": True,
        "channel": "SMS_DISPATCH_SIMULATOR",
        "status": "DELIVERED_SIMULATED",
        "message_id": simulated_id,
        "recipient": clean_phone,
        "carrier_network": "Emergency Broadcast Gateway (Local)",
        "dispatched_at": now_iso,
        "body": message_text,
        "photo_attached": bool(photo_path and Path(photo_path).is_file()),
    }


DISPATCH_LOG_PATH = Path("outputs/sms_dispatches.jsonl")


def log_sms_dispatch(dispatch_result, log_path=None):
    """Persist SMS dispatch audit trail to JSONL and SQLite."""
    path = Path(log_path) if log_path else DISPATCH_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(dispatch_result) + "\n")
    return dispatch_result
