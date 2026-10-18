import pytest
from src.alert_dispatcher import format_emergency_sms, sanitize_phone_number, dispatch_sms, log_sms_dispatch


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
    msg = format_emergency_sms(mock_event, camera_name="Junction #10")
    assert "PI-0004" in msg
    assert "6.61s" in msg
    assert "35, 83" in msg
    assert "10.1px" in msg
    assert "Junction #10" in msg


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


if __name__ == "__main__":
    test_sanitize_phone_number_valid()
    test_sanitize_phone_number_invalid()
    test_format_emergency_sms()
    print("All alert dispatcher tests passed!")
