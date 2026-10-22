import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.alert_dispatcher import (
    format_emergency_sms,
    sanitize_phone_number,
    dispatch_sms,
    log_sms_dispatch,
    check_dispatch_cooldown,
    reset_dispatch_cooldowns,
)


def test_sanitize_phone_number_valid():
    assert sanitize_phone_number("+91 98765 43210") == "+919876543210"
    assert sanitize_phone_number("123-456-7890") == "1234567890"
    assert sanitize_phone_number("+1 (555) 234-5678") == "+15552345678"


def test_sanitize_phone_number_invalid():
    with pytest.raises(ValueError):
        sanitize_phone_number("abc")

    with pytest.raises(ValueError):
        sanitize_phone_number("123")  # too short


def test_format_emergency_sms():
    mock_event = {
        "event_id": "PI-0004",
        "evidence_timestamp_seconds": 6.607,
        "track_ids": [35, 83],
        "minimum_distance_px": 10.12,
        "peak_closing_speed_px_per_second": 54.68,
    }
    msg = format_emergency_sms(
        mock_event,
        camera_name="Junction #10",
        camera_id="CAM-99",
        location_details="Northbound lane 2",
    )
    assert "PI-0004" in msg
    assert "6.61s" in msg
    assert "35, 83" in msg
    assert "10.1px" in msg
    assert "Junction #10" in msg
    assert "CAM-99" in msg
    assert "Northbound lane 2" in msg
    assert "Investigation Support Dossier" in msg
    assert "http://localhost:8501" in msg


def test_format_emergency_sms_custom_dossier_link():
    mock_event = {
        "event_id": "PI-0004",
        "evidence_timestamp_seconds": 6.6,
        "track_ids": [35, 83],
    }
    custom_url = "https://ops.motionguard.ai/dossiers/MG-2026-99"
    msg = format_emergency_sms(
        mock_event,
        dossier_link=custom_url,
    )
    assert f"Investigation Support Dossier: {custom_url}" in msg


def test_simulated_dispatch(tmp_path):
    mock_event = {
        "event_id": "PI-0001",
        "evidence_timestamp_seconds": 3.6,
        "track_ids": [29, 31],
        "minimum_distance_px": 56.8,
        "peak_closing_speed_px_per_second": 19.5,
    }
    msg = format_emergency_sms(mock_event)
    result = dispatch_sms("+919876543210", msg, gateway_mode="SIMULATOR")
    assert result["success"] is True
    assert result["channel"] == "SMS_DISPATCH_SIMULATOR"
    assert result["recipient"] == "+919876543210"
    assert "SMS-SIM-" in result["message_id"]

    log_file = tmp_path / "test_dispatch.jsonl"
    log_sms_dispatch(result, log_path=str(log_file))
    assert log_file.is_file()
    assert "+919876543210" in log_file.read_text()


def test_cooldown_rate_limit():
    reset_dispatch_cooldowns()
    cam = "CAM-TEST-01"
    # First dispatch allowed
    assert check_dispatch_cooldown(cam, cooldown_seconds=60, threat_score=40, threat_level="HIGH") is True
    # Immediate second dispatch with same severity throttled
    assert check_dispatch_cooldown(cam, cooldown_seconds=60, threat_score=40, threat_level="HIGH") is False

    # Throttled dispatch returns rate limited result
    res = dispatch_sms(
        "+919876543210",
        "Test message",
        camera_id=cam,
        threat_score=40,
        threat_level="HIGH",
        cooldown_seconds=60,
        gateway_mode="SIMULATOR",
    )
    assert res["success"] is False
    assert res["status"] == "RATE_LIMITED"

    # Severity escalation (CRITICAL collision score 95) bypasses active cooldown!
    res_esc = dispatch_sms(
        "+919876543210",
        "CRITICAL ESCALATED COLLISION",
        camera_id=cam,
        threat_score=95,
        threat_level="CRITICAL",
        cooldown_seconds=60,
        gateway_mode="SIMULATOR",
    )
    assert res_esc["success"] is True


@patch("src.alert_dispatcher.requests.post")
def test_mock_twilio_dispatch(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"sid": "SM123456789fake"}
    mock_post.return_value = mock_resp

    res = dispatch_sms(
        phone_number="+15551234567",
        message_text="Emergency test alert",
        twilio_sid="ACfake_sid",
        twilio_token="fake_token",
        twilio_from="+15559876543",
        gateway_mode="TWILIO",
    )
    assert res["success"] is True
    assert res["channel"] == "TWILIO_SMS"
    assert res["message_id"] == "SM123456789fake"
    assert mock_post.called


@patch("src.alert_dispatcher.requests.post")
def test_mock_telegram_text_dispatch(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"result": {"message_id": 98765}}
    mock_post.return_value = mock_resp

    res = dispatch_sms(
        phone_number="+919876543210",
        message_text="Telegram alert",
        telegram_token="fake_bot_token",
        telegram_chat_id="123456",
        gateway_mode="TELEGRAM",
    )
    assert res["success"] is True
    assert res["channel"] == "TELEGRAM_ALERT"
    assert res["message_id"] == "98765"
    assert res["photo_attached"] is False
    assert "sendMessage" in mock_post.call_args[0][0]


@patch("src.alert_dispatcher.requests.post")
def test_mock_telegram_photo_dispatch(mock_post, tmp_path):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"result": {"message_id": 99999}}
    mock_post.return_value = mock_resp

    photo_file = tmp_path / "snapshot.jpg"
    photo_file.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00")

    res = dispatch_sms(
        phone_number="+919876543210",
        message_text="Telegram photo alert",
        telegram_token="fake_bot_token",
        telegram_chat_id="123456",
        photo_path=str(photo_file),
        gateway_mode="TELEGRAM",
    )
    assert res["success"] is True
    assert res["channel"] == "TELEGRAM_ALERT"
    assert res["message_id"] == "99999"
    assert res["photo_attached"] is True
    assert "sendPhoto" in mock_post.call_args[0][0]


@patch("src.alert_dispatcher.requests.post")
def test_mock_telegram_dispatch_includes_dossier_link(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"result": {"message_id": 12345}}
    mock_post.return_value = mock_resp

    mock_event = {
        "event_id": "PI-0999",
        "evidence_timestamp_seconds": 4.5,
        "track_ids": [10, 20],
        "minimum_distance_px": 5.0,
        "peak_closing_speed_px_per_second": 30.0,
    }
    dossier_url = "https://ops.motionguard.ai/investigation_dossiers/PI-0999.pdf"
    msg = format_emergency_sms(mock_event, dossier_link=dossier_url)

    res = dispatch_sms(
        phone_number="+919876543210",
        message_text=msg,
        telegram_token="fake_bot_token",
        telegram_chat_id="123456",
        gateway_mode="TELEGRAM",
    )
    assert res["success"] is True
    assert "sendMessage" in mock_post.call_args[0][0]
    payload = mock_post.call_args[1]["json"]
    assert f"Investigation Support Dossier: {dossier_url}" in payload["text"]
