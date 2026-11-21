# geospatial_engine.py
# ==============================================================================
# NIRVYTH Geospatial Tactical Intelligence (GEOINT) & Intercept Engine
# Calculates Haversine distances, ETA & nearest Dial 112 / PCR vehicle routing.
# ==============================================================================

import math
from config import PATROL_UNITS

class GeospatialEngine:
    def __init__(self):
        self.patrol_units = list(PATROL_UNITS)

    def haversine_distance_meters(self, lat1, lon1, lat2, lon2):
        """Calculates great-circle distance between two GPS coordinates in meters."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    def find_nearest_patrol_unit(self, incident_lat, incident_lon):
        """Identifies closest available UP112 / PCR vehicle and estimates ETA."""
        best_unit = None
        min_dist_m = float("inf")

        for unit in self.patrol_units:
            dist_m = self.haversine_distance_meters(incident_lat, incident_lon, unit["lat"], unit["lon"])
            if dist_m < min_dist_m:
                min_dist_m = dist_m
                best_unit = unit

        # Realistic urban patrol speed: 35 km/h (9.72 m/s) with 1.25 road curvature factor
        speed_mps = 9.72
        effective_dist_m = min_dist_m * 1.25
        eta_seconds = max(25, int(effective_dist_m / speed_mps))
        mins = eta_seconds // 60
        secs = eta_seconds % 60
        eta_str = f"{mins}m {secs:02d}s" if mins > 0 else f"{secs}s"

        return {
            "selected_unit": best_unit,
            "straight_distance_meters": round(min_dist_m, 1),
            "estimated_road_meters": round(effective_dist_m, 1),
            "eta_formatted": eta_str,
            "eta_seconds": eta_seconds,
            "target_lat": incident_lat,
            "target_lon": incident_lon
        }

    def get_tactical_zones(self):
        """Returns tactical GeoJSON polygon features for Greater Noida / Knowledge Park."""
        return [
            {
                "zone_id": "ZONE_RED_01",
                "name": "High-Security VIP Stage & Exhibition Arena (Knowledge Park)",
                "risk_tier": "CRITICAL_RED",
                "color": "#ef4444",
                "center": [28.4675, 77.4950]
            },
            {
                "zone_id": "ZONE_AMBER_02",
                "name": "Crowd Choke Point - Knowledge Park II Metro Interchange",
                "risk_tier": "CROWD_WATCH_AMBER",
                "color": "#f59e0b",
                "center": [28.4705, 77.4920]
            },
            {
                "zone_id": "ZONE_GREEN_03",
                "name": "Designated Medical Evacuation & Safe Assembly Area (Expo Mart)",
                "risk_tier": "SAFE_HAVEN_GREEN",
                "color": "#10b981",
                "center": [28.4720, 77.4990]
            }
        ]
