"""
Tests for src/prune_gateway.py
"""

import os
from unittest.mock import patch, MagicMock
from src.prune_gateway import prune_nominal_candidates, generate_prune_triage_summary


def test_prune_nominal_candidates_empty():
    assert prune_nominal_candidates([]) == []


def test_prune_nominal_candidates_filtering():
    def mock_scorer(event):
        return {"threat_score": event.get("score", 0)}

    events = [
        {"event_id": "EVT-1", "score": 10},
        {"event_id": "EVT-2", "score": 30},
        {"event_id": "EVT-3", "score": 85},
    ]

    filtered = prune_nominal_candidates(events, min_threat_score=25.0, risk_scorer=mock_scorer)
    assert len(filtered) == 2
    assert filtered[0]["event_id"] == "EVT-2"
    assert filtered[1]["event_id"] == "EVT-3"
    assert filtered[0]["prune_filtered"] is False
    assert filtered[0]["prune_assessed_score"] == 30


def test_generate_prune_triage_summary_simulator():
    event = {
        "event_id": "EVT-001",
        "minimum_distance_px": 12.5,
        "peak_closing_speed_px_per_second": 45.2,
    }
    risk_result = {
        "threat_score": 75,
        "threat_level": "HIGH",
    }

    # Test simulator mode (no API key)
    with patch.dict(os.environ, {"PRUNE_API_KEY": ""}):
        result = generate_prune_triage_summary(event, risk_result, gateway_mode="SIMULATOR")
        assert result["status"] == "SIMULATED"
        assert result["gateway"] == "PRUNE_SIMULATOR"
        assert "EVT-001" in result["triage_summary"]
        assert "75/100" in result["triage_summary"]
        assert "12.50 px" in result["triage_summary"]


def test_generate_prune_triage_summary_live_mocked():
    event = {
        "event_id": "EVT-002",
        "minimum_distance_px": 8.0,
        "peak_closing_speed_px_per_second": 60.0,
    }
    risk_result = {
        "threat_score": 90,
        "threat_level": "CRITICAL",
    }

    mock_response_data = {
        "choices": [
            {
                "message": {
                    "content": "Operator alert: High-threat collision candidate detected at 8.00 px separation."
                }
            }
        ],
        "usage": {"total_tokens": 42},
    }

    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"choices":[{"message":{"content":"Mocked LLM triage note"}}],"usage":{"tokens":15}}'
    mock_resp.__enter__.return_value = mock_resp

    with patch.dict(os.environ, {"PRUNE_API_KEY": "prune_test_key_123"}):
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = generate_prune_triage_summary(event, risk_result, gateway_mode="LIVE")
            assert result["status"] == "SUCCESS"
            assert result["gateway"] == "PRUNE_LIVE_GATEWAY"
            assert "Mocked LLM triage note" in result["triage_summary"]
