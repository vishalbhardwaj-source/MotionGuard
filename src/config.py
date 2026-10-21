import os
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

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
    "zones": {
        "enabled": True,
        "merge_zone_sensitivity": 0.65,
        "shoulder_sensitivity": 1.80,
    },
    "severity": {
        "stopped_vehicle_seconds": 2.0,
        "stopped_speed_px_s": 5.0,
        "near_miss_max_ttc": 3.5,
        "near_miss_max_norm_dist": 1.8,
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
        "default_phone": "+15550199000",
        "auto_dispatch_critical_only": True,
        "gateway_mode": "SIMULATOR",
    },
}


def _parse_yaml_val(val_str):
    val_str = val_str.strip()
    if val_str.startswith("[") and val_str.endswith("]"):
        items = val_str[1:-1].split(",")
        return [_parse_yaml_val(it) for it in items if it.strip()]
    if val_str.lower() == "true":
        return True
    if val_str.lower() == "false":
        return False
    try:
        if "." in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str.strip('"').strip("'")


def _fallback_parse_yaml(text):
    result = {}
    current_section = None
    for raw_line in text.splitlines():
        line = raw_line.split("#")[0].rstrip()
        if not line:
            continue
        if not line.startswith(" ") and not line.startswith("\t") and ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val:
                result[key] = _parse_yaml_val(val)
                current_section = None
            else:
                result[key] = {}
                current_section = key
        elif current_section is not None and ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val:
                result[current_section][key] = _parse_yaml_val(val)
    return result


def load_config(config_path=None):
    """Load configuration YAML with fallback to default parameters."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    import copy
    config = copy.deepcopy(DEFAULTS)

    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                if yaml is not None:
                    loaded = yaml.safe_load(content)
                else:
                    loaded = _fallback_parse_yaml(content)

                if isinstance(loaded, dict):
                    for section, values in loaded.items():
                        if section in config and isinstance(values, dict):
                            config[section].update(values)
                        else:
                            config[section] = values
        except Exception:
            pass

    return config
