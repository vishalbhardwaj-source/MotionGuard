from pathlib import Path
from src.config import load_config


def test_load_config_defaults():
    config = load_config()
    assert "vision" in config
    assert "kinematics" in config
    assert "risk_engine" in config
    assert "dispatch" in config
    assert config["kinematics"]["max_ttc_seconds"] == 3.5
    assert config["kinematics"]["max_normalized_distance"] == 1.8
    assert config["vision"]["vehicle_classes"] == [2, 3, 5, 7]


def test_load_config_custom_file(tmp_path):
    custom_yaml = tmp_path / "custom_config.yaml"
    custom_yaml.write_text("kinematics:\n  max_ttc_seconds: 1.5\n", encoding="utf-8")
    cfg = load_config(custom_yaml)
    assert cfg["kinematics"]["max_ttc_seconds"] == 1.5
    # Defaults remain for other sections
    assert cfg["vision"]["imgsz"] == 640
