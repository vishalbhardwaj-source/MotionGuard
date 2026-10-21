import datetime
import json
import os
import re
from pathlib import Path
import requests

# Per-camera dispatch cooldown cache (seconds)
_DISPATCH_COOLDOWN_CACHE = {}


def check_dispatch_cooldown(camera_id="DEFAULT_CAMERA", cooldown_seconds=60):
    """
    Check and enforce per-camera alert rate limits.
    Returns True if dispatch is allowed, False if within cooldown period.
    """
    now = datetime.datetime.now().timestamp()
    last_time = _DISPATCH_COOLDOWN_CACHE.get(camera_id, 0.0)
    if (now - last_time) < cooldown_seconds:
        return False
    _DISPATCH_COOLDOWN_CACHE[camera_id] = now
    return True


def reset_dispatch_cooldowns():
    """Clear in-memory dispatch cooldowns (useful for tests)."""
    _DISPATCH_COOLDOWN_CACHE.clear()


def format_emergency_sms(
    event,
    camera_name="Highway North - Sector 4",
    camera_id="CAM-01",
    location_details="Mile Marker 14.2 / Sector 4",
    incident_type="POTENTIAL ACCIDENT / HIGH-RISK INTERACTION",
):
    """
    Format a structured emergency dispatch message for traffic authorities and first responders.
    Includes incident ID, camera ID, geographic location, video timestamps, and kinematics.
    """
    event_id = event.get("event_id", "EVT-UNKNOWN")
    timestamp = event.get("evidence_timestamp_seconds")
    if timestamp is None:
        timestamp = event.get("minimum_distance_timestamp_seconds", event.get("start_seconds", 0.0))

    try:
        time_str = f"{float(timestamp):.2f}s"
    except (ValueError, TypeError):
        time_str = str(timestamp)

    tracks = event.get("track_ids", [])
    track_str = ", ".join(map(str, tracks)) if tracks else "Unconfirmed"
    min_dist = event.get("minimum_distance_px", "N/A")
    closing_speed = event.get("peak_closing_speed_px_per_second", "N/A")

    if isinstance(min_dist, (int, float)):
        min_dist_str = f"{min_dist:.1f}px"
    else:
        min_dist_str = str(min_dist)

    if isinstance(closing_speed, (int, float)):
        closing_speed_str = f"{closing_speed:.1f}px/s"
    else:
        closing_speed_str = str(closing_speed)

    message = (
        f"🚨 MOTIONGUARD EMERGENCY DISPATCH ALERT 🚨\n"
        f"Incident: {event_id} ({incident_type})\n"
        f"Camera ID: {camera_id} | Location: {camera_name} ({location_details})\n"
        f"Video Timestamp: {time_str}\n"
        f"Involved Tracks: {track_str}\n"
        f"Kinematics: Closest Sep {min_dist_str} | Peak Closing {closing_speed_str}\n"
        f"Action: Forensic decision-support candidate flagged for immediate operator review at http://localhost:8501"
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
    camera_id=None,
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

    # Rate limiting / cooldown check
    if cooldown_seconds and camera_id:
        if not check_dispatch_cooldown(camera_id, cooldown_seconds):
            return {
                "success": False,
                "channel": "RATE_LIMIT_COOLDOWN",
                "status": "RATE_LIMITED",
                "error": f"Dispatch throttled: Camera {camera_id} is in cooldown ({cooldown_seconds}s limit).",
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

        try:
            if has_photo:
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


def log_sms_dispatch(dispatch_result, log_path="outputs/sms_dispatches.jsonl"):
    """Persist SMS dispatch audit trail to JSONL."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(dispatch_result) + "\n")
    return dispatch_result
