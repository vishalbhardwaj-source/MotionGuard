import pytest
from src.zones import (
    point_in_polygon,
    Zone,
    get_default_highway_zones,
    find_zone_for_point,
    get_contextual_threshold_multiplier,
)
from src.interaction_analysis import analyze_interactions


def test_point_in_polygon_square():
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert point_in_polygon((5.0, 5.0), square) is True
    assert point_in_polygon((15.0, 5.0), square) is False
    assert point_in_polygon((-1.0, 5.0), square) is False


def test_default_highway_zones():
    zones = get_default_highway_zones(frame_width=1000, frame_height=500)
    assert len(zones) == 4

    zone_types = {z.zone_type for z in zones}
    assert "SHOULDER" in zone_types
    assert "REGULAR_LANE" in zone_types
    assert "MERGE_ZONE" in zone_types

    z_lane = find_zone_for_point((300.0, 250.0), zones)
    assert z_lane is not None
    assert z_lane.zone_type == "REGULAR_LANE"

    z_merge = find_zone_for_point((750.0, 250.0), zones)
    assert z_merge is not None
    assert z_merge.zone_type == "MERGE_ZONE"


def test_contextual_threshold_multiplier():
    zones = get_default_highway_zones(frame_width=1000, frame_height=500)
    lane_zone = next(z for z in zones if z.zone_type == "REGULAR_LANE")
    merge_zone = next(z for z in zones if z.zone_type == "MERGE_ZONE")
    shoulder_zone = next(z for z in zones if z.zone_type == "SHOULDER")

    mult, reason = get_contextual_threshold_multiplier(lane_zone, lane_zone)
    assert mult == 1.0

    mult_m, reason_m = get_contextual_threshold_multiplier(merge_zone, merge_zone)
    assert mult_m == 0.65
    assert "MERGE" in reason_m

    mult_s, reason_s = get_contextual_threshold_multiplier(shoulder_zone, lane_zone)
    assert mult_s == 1.8
    assert "SHOULDER" in reason_s


def test_zones_in_interaction_analysis():
    zones = [
        Zone(
            name="Test Merge Zone",
            zone_type="MERGE_ZONE",
            polygon=[(0, 0), (300, 0), (300, 300), (0, 300)],
            sensitivity_multiplier=0.5, # halves proximity threshold from 70px to 35px
        )
    ]
    # Two vehicles closing in from distance 60px down to 50px
    # Distances are between 50px and 60px.
    # Without zones (threshold 70px): 50-60px <= 70px -> triggers candidate finding.
    # With merge zone (threshold 35px): 50-60px > 35px -> safe merge tolerance, 0 findings!
    records = []
    for f in range(5):
        t = f * 0.1
        # Track 1 moves right: 40, 42, 44, 46, 48
        # Track 2 moves left: 100, 97, 94, 91, 88
        # Distance: 60, 55, 50, 45, 40 (all within 40-60px)
        c1 = 40.0 + f * 2.0
        c2 = 100.0 - f * 3.0
        records.append({
            "frame_index": f,
            "timestamp_seconds": t,
            "track_id": 1,
            "center_xy": (c1, 100.0),
            "bbox_xyxy": [c1 - 10, 90, c1 + 10, 110],
        })
        records.append({
            "frame_index": f,
            "timestamp_seconds": t,
            "track_id": 2,
            "center_xy": (c2, 100.0),
            "bbox_xyxy": [c2 - 10, 90, c2 + 10, 110],
        })

    # Without zones: distance <= 70px -> candidate findings detected
    findings_no_zone = analyze_interactions(
        records, proximity_threshold_px=70.0, min_closing_speed_px_s=1.0, min_consecutive_matches=2
    )
    assert len(findings_no_zone) > 0

    # With merge zone: threshold = 70 * 0.5 = 35px. Distances >= 40px are safely tolerated!
    findings_with_zone = analyze_interactions(
        records, proximity_threshold_px=70.0, min_closing_speed_px_s=1.0, min_consecutive_matches=2, zones=zones
    )
    assert len(findings_with_zone) == 0
