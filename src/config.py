import os
from pathlib import Path
import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

DEFAULTS = {
    "vision": {
        "model_weights": "yolo11n.pt",
        "imgsz": 640,
        "confidence": 0.25,
        "tracker": "bytetrack.yaml",
        "vehicle_classes": [2, 3, 5, 7],
        "frame_skip": 0,
    },
    "kinematics": {
        "proximity_threshold_px": 80.0,
        "min_closing_speed_px_s": 5.0,
        "max_gap_seconds": 0.2,
        "min_consecutive_matches": 3,
        "max_ttc_seconds": 3.5,
        "max_normalized_distance": 1.8,
        "min_iou_contact": 0.05,
        "deceleration_post_impact_threshold": 0.50,
    },
    "risk_engine": {
        "speed_limit_kmh": 50.0,
        "critical_threat_score": 80,
        "high_threat_score": 60,
        "elevated_threat_score": 40,
    },
    "dispatch": {
        "cooldown_seconds": 60,
        "default_camera_id": "CAM-01",
        "default_location": "Highway North - Sector 4",
        "default_phone": "+919876543210",
        "auto_dispatch_critical_only": True,
        "gateway_mode": "SIMULATOR",
    },
}


def load_config(config_path=None):
    """Load configuration YAML with fallback to default parameters."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    config = dict(DEFAULTS)

    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as file:
                loaded = yaml.safe_load(file)
                if isinstance(loaded, dict):
                    for section, values in loaded.items():
                        if section in config and isinstance(values, dict):
                            config[section].update(values)
                        else:
                            config[section] = values
        except Exception as exc:
            print(f"Warning: Could not read config file ({exc}). Using defaults.")

    return config
