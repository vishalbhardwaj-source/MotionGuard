"""
MotionGuard — Spatial Geofencing & Zone Management
Defines operational road zones (lanes, merge acceleration zones, shoulders, intersections)
and modulates kinematic risk thresholds based on spatial context.
"""

from typing import List, Dict, Any, Optional, Tuple


def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Determine if a 2D point (x, y) is inside a polygon using ray-casting.
    Pure Python implementation with no external C dependencies.
    """
    if not polygon or len(polygon) < 3:
        return False

    x, y = point
    inside = False
    n = len(polygon)

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_inters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= x_inters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


class Zone:
    """Represents a spatial region of interest with specific operational sensitivity."""

    def __init__(
        self,
        name: str,
        zone_type: str,
        polygon: List[Tuple[float, float]],
        sensitivity_multiplier: float = 1.0,
        description: str = "",
        color_hex: str = "#3B82F6",
    ):
        self.name = name
        self.zone_type = zone_type.upper()  # REGULAR_LANE, MERGE_ZONE, SHOULDER, INTERSECTION
        self.polygon = polygon
        self.sensitivity_multiplier = float(sensitivity_multiplier)
        self.description = description
        self.color_hex = color_hex

    def contains_point(self, point_xy: Tuple[float, float]) -> bool:
        return point_in_polygon(point_xy, self.polygon)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "zone_type": self.zone_type,
            "polygon": self.polygon,
            "sensitivity_multiplier": self.sensitivity_multiplier,
            "description": self.description,
            "color_hex": self.color_hex,
        }


def get_default_highway_zones(frame_width: int = 1280, frame_height: int = 720) -> List[Zone]:
    """
    Generate standard default highway zones mapped to standard aspect ratios:
    - Left Shoulder (Emergency)
    - Through Lanes (Normal traffic)
    - On-Ramp Merge Zone (Higher proximity tolerance)
    - Right Shoulder (Breakdown / Hazard)
    """
    w, h = float(frame_width), float(frame_height)

    return [
        Zone(
            name="Emergency Shoulder (Left)",
            zone_type="SHOULDER",
            polygon=[(0.0, 0.0), (w * 0.15, 0.0), (w * 0.12, h), (0.0, h)],
            sensitivity_multiplier=1.8,
            description="Left emergency breakdown lane. Stationary vehicles or swerves indicate urgent hazard.",
            color_hex="#EF4444",
        ),
        Zone(
            name="Through Traffic (Lanes 1 & 2)",
            zone_type="REGULAR_LANE",
            polygon=[(w * 0.15, 0.0), (w * 0.65, 0.0), (w * 0.60, h), (w * 0.12, h)],
            sensitivity_multiplier=1.0,
            description="Main through-lanes with regular operating distance thresholds.",
            color_hex="#10B981",
        ),
        Zone(
            name="Acceleration / Merge Zone",
            zone_type="MERGE_ZONE",
            polygon=[(w * 0.65, 0.0), (w * 0.88, 0.0), (w * 0.85, h), (w * 0.60, h)],
            sensitivity_multiplier=0.65,
            description="On-ramp convergence area. Vehicles naturally merge closely; proximity threshold is scaled.",
            color_hex="#F59E0B",
        ),
        Zone(
            name="Hard Shoulder (Right)",
            zone_type="SHOULDER",
            polygon=[(w * 0.88, 0.0), (w, 0.0), (w, h), (w * 0.85, h)],
            sensitivity_multiplier=2.0,
            description="Right breakdown shoulder. High sensitivity for stopped vehicles.",
            color_hex="#DC2626",
        ),
    ]


def find_zone_for_point(point_xy: Tuple[float, float], zones: Optional[List[Zone]]) -> Optional[Zone]:
    """Identify which operational zone encompasses a given (x, y) coordinate."""
    if not zones or not point_xy:
        return None
    for zone in zones:
        if zone.contains_point(point_xy):
            return zone
    return None


def get_contextual_threshold_multiplier(
    zone_a: Optional[Zone],
    zone_b: Optional[Zone],
) -> Tuple[float, str]:
    """
    Determine threshold modulation factor based on spatial context:
    - Merge Zone interaction: Multiplier < 1.0 (requires closer proximity to trigger, preventing false alarms).
    - Shoulder interaction: Multiplier > 1.0 (escalates sensitivity).
    - Regular lanes: Multiplier = 1.0.
    """
    if zone_a is None and zone_b is None:
        return 1.0, "STANDARD_UNZONED"

    types = {z.zone_type for z in (zone_a, zone_b) if z is not None}

    if "SHOULDER" in types:
        mult = max(z.sensitivity_multiplier for z in (zone_a, zone_b) if z is not None)
        return mult, "SHOULDER_HAZARD"
    if types == {"MERGE_ZONE"}:
        mult = min(z.sensitivity_multiplier for z in (zone_a, zone_b) if z is not None)
        return mult, "MERGE_CONVERGENCE_ZONE"
    if "MERGE_ZONE" in types:
        return 0.80, "LANE_MERGE_TRANSITION"

    return 1.0, "NOMINAL_LANE_FLOW"
