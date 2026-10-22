"""
Tests for src/gemini_service.py
"""

import os
from unittest.mock import patch, MagicMock
from src.gemini_service import (
    load_env_file,
    get_gemini_api_key,
    test_gemini_connection as check_gemini_connection,
    generate_gemini_triage_analysis,
    _encode_image_to_base64,
)


def test_get_gemini_api_key_from_env():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_gemini_key_123"}):
        assert get_gemini_api_key() == "test_gemini_key_123"


def test_get_gemini_api_key_fallback_to_prune():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "", "PRUNE_API_KEY": "AQ.dummy_key"}):
        assert get_gemini_api_key() == "AQ.dummy_key"


def test_gemini_connection_unconfigured():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "", "PRUNE_API_KEY": ""}):
        result = check_gemini_connection()
        assert result["status"] == "UNCONFIGURED"


def test_generate_gemini_triage_analysis_offline_fallback():
    event = {
        "event_id": "EVT-TEST",
        "minimum_distance_px": 15.0,
        "peak_closing_speed_px_per_second": 30.0,
        "track_id_1": 1,
        "track_id_2": 2,
    }
    risk_result = {"threat_score": 50, "threat_level": "ELEVATED"}

    with patch.dict(os.environ, {"GEMINI_API_KEY": "", "PRUNE_API_KEY": ""}):
        res = generate_gemini_triage_analysis(event, risk_result)
        assert res["status"] == "SIMULATED"
        assert res["threat_score"] == 50
        assert "EVT-TEST" in res["summary"]


def test_generate_gemini_triage_analysis_mock_success():
    event = {
        "event_id": "EVT-MOCK",
        "minimum_distance_px": 5.0,
        "peak_closing_speed_px_per_second": 80.0,
    }
    risk_result = {"threat_score": 95, "threat_level": "CRITICAL"}

    mock_resp = MagicMock()
    mock_resp.read.return_value = (
        b'{"candidates": [{"content": {"parts": [{"text": "Critical impact imminent between vehicles."}]}}]}'
    )
    mock_resp.__enter__.return_value = mock_resp

    with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSyFakeKey"}):
        with patch("urllib.request.urlopen", return_value=mock_resp):
            res = generate_gemini_triage_analysis(event, risk_result)
            assert res["status"] == "SUCCESS"
            assert "Critical impact imminent" in res["summary"]
            assert res["threat_score"] == 95
