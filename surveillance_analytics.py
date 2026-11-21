# surveillance_analytics.py
"""
NIRVYTH Live Law-and-Order Surveillance Analytics Engine
Monitors crowd density, stampede early warnings, violent brawls, and perimeter breaches.
"""

import random
import time
from config import ANALYTICS_THRESHOLDS

class SurveillanceAnalyticsEngine:
    def __init__(self):
        self.crowd_density = 2.4  # persons per sq. meter
        self.violence_score = 0.12 # 0.0 to 1.0
        self.stampede_risk = "NORMAL"
        self.perimeter_status = "SECURE"
        self.detected_persons_count = 142
        self.active_anomalies = []

    def analyze_frame_dynamics(self, scenario_trigger=None):
        """Computes crowd kinetics, optical flow divergence, and anomaly flags."""
        timestamp = time.strftime("%H:%M:%S")

        # Check for simulated incident triggers
        if scenario_trigger == "CROWD_SURGE":
            self.crowd_density = round(min(5.8, self.crowd_density + 0.9), 2)
            self.detected_persons_count += 35
        elif scenario_trigger == "VIOLENCE_FIGHT":
            self.violence_score = 0.92
        elif scenario_trigger == "PERIMETER_BREACH":
            self.perimeter_status = "BREACH_DETECTED"
        elif scenario_trigger == "RESET_NORMAL":
            self.crowd_density = 2.4
            self.violence_score = 0.14
            self.perimeter_status = "SECURE"
        else:
            # Natural micro-fluctuation
            self.crowd_density = round(max(1.5, min(5.5, self.crowd_density + random.uniform(-0.15, 0.15))), 2)
            self.violence_score = round(max(0.05, min(0.95, self.violence_score + random.uniform(-0.03, 0.03))), 2)

        # Assess Stampede / Density Risk
        if self.crowd_density >= ANALYTICS_THRESHOLDS["crowd_density_critical"]:
            self.stampede_risk = "CRITICAL_STAMPEDE_WARNING"
            severity = "CRITICAL"
            msg = f"Stampede Risk Alert: High Density ({self.crowd_density} persons/m2) at Metro Gate 4 Choke Point!"
        elif self.crowd_density >= ANALYTICS_THRESHOLDS["crowd_density_warning"]:
            self.stampede_risk = "ELEVATED_MONITORING"
            severity = "WARNING"
            msg = f"Crowd Surge Warning: Density reached {self.crowd_density} persons/m2."
        else:
            self.stampede_risk = "NOMINAL_SAFE"
            severity = "NORMAL"
            msg = "Crowd movement within safe operational parameters."

        anomalies = []
        if self.stampede_risk != "NOMINAL_SAFE":
            anomalies.append({
                "type": "CROWD_DENSITY_SURGE",
                "severity": severity,
                "message": msg,
                "density_value": self.crowd_density,
                "time": timestamp
            })

        if self.violence_score >= ANALYTICS_THRESHOLDS["violence_motion_threshold"]:
            anomalies.append({
                "type": "VIOLENCE_SCUFFLE_DETECTED",
                "severity": "CRITICAL",
                "message": f"Violence Anomaly: Spatio-temporal motion divergence ({int(self.violence_score*100)}% confidence).",
                "violence_score": self.violence_score,
                "time": timestamp
            })

        if self.perimeter_status == "BREACH_DETECTED":
            anomalies.append({
                "type": "RED_ZONE_PERIMETER_BREACH",
                "severity": "HIGH",
                "message": "Tripwire Alarm: Unauthorized ingress into VIP Enclosure North Cordon.",
                "time": timestamp
            })

        self.active_anomalies = anomalies

        return {
            "crowd_density": self.crowd_density,
            "detected_persons_count": self.detected_persons_count,
            "violence_score": self.violence_score,
            "stampede_risk": self.stampede_risk,
            "perimeter_status": self.perimeter_status,
            "anomalies": anomalies,
            "timestamp": timestamp
        }
