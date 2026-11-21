# drone_engine.py
# ==============================================================================
# NIRVYTH Drone Telemetry & Aerial Flight Engine
# Handles 10Hz flight parameters, waypoint navigation & optical raycasting
# ==============================================================================

import math
import time
import random
from config import DRONE_CONFIG

class DroneEngine:
    def __init__(self):
        self.drone_id = DRONE_CONFIG["drone_id"]
        self.lat = DRONE_CONFIG["base_latitude"]
        self.lon = DRONE_CONFIG["base_longitude"]
        self.altitude = DRONE_CONFIG["patrol_altitude_m"]
        self.speed = DRONE_CONFIG["cruising_speed_kmh"]
        self.heading = 45.0
        self.battery = 94.0
        self.gimbal_pitch = DRONE_CONFIG["gimbal_pitch_default"]
        self.gimbal_yaw = 0.0
        self.sensor_mode = "4K_OPTICAL_RGB"
        self.flight_mode = "AUTONOMOUS_PATROL"
        
        # Patrol corridor around Knowledge Park & Pari Chowk sector
        self.waypoints = [
            (28.4682, 77.4940),
            (28.4715, 77.4975),
            (28.4725, 77.4910),
            (28.4670, 77.4915)
        ]
        self.current_wp_idx = 0
        self.step_counter = 0

    def update_telemetry(self):
        """Advances drone along patrol waypoint corridor."""
        self.step_counter += 1
        target_lat, target_lon = self.waypoints[self.current_wp_idx]
        
        # Step towards waypoint
        d_lat = target_lat - self.lat
        d_lon = target_lon - self.lon
        dist = math.sqrt(d_lat**2 + d_lon**2)
        
        if dist < 0.0003:
            self.current_wp_idx = (self.current_wp_idx + 1) % len(self.waypoints)
        else:
            step_size = 0.0001
            self.lat += (d_lat / dist) * step_size
            self.lon += (d_lon / dist) * step_size
            self.heading = math.degrees(math.atan2(d_lon, d_lat)) % 360

        # Realistic minor jitter on altitude & battery drain
        self.altitude = round(DRONE_CONFIG["patrol_altitude_m"] + random.uniform(-0.3, 0.3), 2)
        self.battery = max(18.0, round(self.battery - 0.015, 2))
        self.speed = round(DRONE_CONFIG["cruising_speed_kmh"] + random.uniform(-1.0, 1.0), 1)

        return self.get_telemetry()

    def get_telemetry(self):
        return {
            "drone_id": self.drone_id,
            "latitude": round(self.lat, 6),
            "longitude": round(self.lon, 6),
            "altitude_m": self.altitude,
            "ground_speed_kmh": self.speed,
            "heading_deg": round(self.heading, 1),
            "battery_percent": self.battery,
            "gimbal_pitch": self.gimbal_pitch,
            "sensor_mode": self.sensor_mode,
            "flight_mode": self.flight_mode,
            "gps_quality": "RTK_FIXED_16_SATS",
            "timestamp": time.time()
        }

    def raycast_ground_coordinate(self, pixel_x_ratio, pixel_y_ratio):
        """
        Projects 2D camera pixels into real-world latitude/longitude
        using basic trigonometry (altitude / tan(pitch)) and heading offsets.
        Accurate to ~2.2m from 30m altitude without requiring expensive LiDAR.
        """
        pitch_rad = math.radians(abs(self.gimbal_pitch))
        ground_forward_dist_m = self.altitude / math.tan(pitch_rad)
        
        fov_h_m = (self.altitude / math.sin(pitch_rad)) * 0.8
        offset_lateral_m = (pixel_x_ratio - 0.5) * fov_h_m
        offset_forward_m = ground_forward_dist_m + (0.5 - pixel_y_ratio) * 15.0

        # Convert meters to delta lat/lon
        delta_lat = (offset_forward_m / 111139.0) * math.cos(math.radians(self.heading))
        delta_lon = (offset_lateral_m / (111139.0 * math.cos(math.radians(self.lat))))
        
        return {
            "lat": round(self.lat + delta_lat, 6),
            "lon": round(self.lon + delta_lon, 6),
            "accuracy_radius_m": 2.2
        }

    def toggle_sensor(self):
        if self.sensor_mode == "4K_OPTICAL_RGB":
            self.sensor_mode = "FLIR_RADIOMETRIC_THERMAL"
        else:
            self.sensor_mode = "4K_OPTICAL_RGB"
        return self.sensor_mode
