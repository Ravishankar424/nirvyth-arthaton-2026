# config.py
# ==============================================================================
# PROJECT NIRVYTH (निर्वीथ) - AI FOR PUBLIC SAFETY & DRONE SURVEILLANCE
# ------------------------------------------------------------------------------
# Hackathon: Arthaton 2026 (hello@arthaton.com)
# Submission Deadline: 22 November 2026, 11:59 PM IST
# Team Name: NIRVYTH
# Team Lead: Ravishankar Kushwaha (rs6816635@gmail.com)
# Team Members: Piyush Jiloka, Sammi Dubey
# ==============================================================================

import os

# --- HACKATHON & SUBMISSION METADATA ---
HACKATHON_METADATA = {
    "project_name": "NIRVYTH (निर्वीथ)",
    "project_tagline": "Autonomous AI & Drone Geospatial Surveillance for Smart Public Safety & Infrastructure Protection",
    "hackathon": "Arthaton 2026",
    "submission_deadline": "22 November 2026, 11:59 PM IST",
    "team_name": "NIRVYTH",
    "team_lead": "Ravishankar Kushwaha (rs6816635@gmail.com)",
    "team_members": [
        "Ravishankar Kushwaha (Lead - Computer Vision, Drone Analytics & Architecture)",
        "Piyush Jiloka (Geospatial GIS Engine & Telemetry Pipeline)",
        "Sammi Dubey (Law-and-Order Analytics & Command UI Dashboard)"
    ],
    "ai_models_used": [
        "YOLOv8 / YOLOv11 (Aerial Pedestrian & Object Detection)",
        "ArcFace 512-Dimensional Vector Embeddings (Angle-Invariant Overhead Biometrics)",
        "Spatio-Temporal Optical Flow Divergence (Crowd Kinetics & Stampede Early Warning)",
        "Trigonometric Camera Raycasting (Camera Pixels to Real-World GPS Projection)"
    ],
    "apis_and_protocols": [
        "Leaflet.js & OpenStreetMap (Tactical GIS Command Grid)",
        "RTSP / MAVLink (Drone Video & 10Hz Flight Telemetry Streaming)",
        "ZeroMQ / WebSockets (Edge-to-Command Metadata Pipeline)",
        "SHA-256 Cryptographic Checksums (BSA 2023 Tamper-Proof Audit Trail)"
    ],
    "demo_url": "http://127.0.0.1:8080",
    "github_repo": "https://github.com/ravishankar-kushwaha/nirvyth-arthaton-2026",
    "youtube_demo": "https://youtu.be/DEMO_VIDEO_ID"
}

# --- SERVER SETTINGS ---
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080

# --- DRONE TELEMETRY CONFIGURATION ---
DRONE_CONFIG = {
    "drone_id": "UAV-SENTINEL-X1",
    "platform": "DJI Matrice 300 RTK / PX4 Enterprise",
    "base_latitude": 28.6315,
    "base_longitude": 77.2185,
    "patrol_altitude_m": 32.5,
    "cruising_speed_kmh": 22.0,
    "sensor_modes": ["4K_OPTICAL_RGB", "FLIR_RADIOMETRIC_THERMAL"],
    "gimbal_pitch_default": -45.0,
    "telemetry_rate_hz": 10,
    "failsafe_battery_threshold": 20.0
}

# --- AI VISION & BIOMETRIC THRESHOLDS ---
FACE_RECOGNITION = {
    "match_threshold": 0.85,           # 85% cosine similarity required to flag a suspect
    "critical_threshold": 0.90,        # 90%+ triggers immediate Priority-1 dispatch
    "embedding_dim": 512,              # ArcFace 512-D vector space
    "dpdp_privacy_masking": True,      # Auto-blur non-watchlist civilians on the edge (DPDP Act 2023)
    "anti_spoofing_enabled": True
}

# --- CROWD KINETICS & LAW-AND-ORDER THRESHOLDS ---
ANALYTICS_THRESHOLDS = {
    "crowd_density_warning": 3.0,      # persons / sq. meter (Amber Alert)
    "crowd_density_critical": 4.5,     # persons / sq. meter (Stampede Risk Siren)
    "violence_motion_threshold": 0.78, # Spatio-temporal motion divergence for scuffles
    "perimeter_breach_dwell_sec": 5.0, # Seconds inside restricted cordon before alarm
    "lead_time_seconds": 14.5          # Early warning lead time before stampede crush
}

# --- GEOSPATIAL PATROL UNITS (PCR VANS) ---
PATROL_UNITS = [
    {
        "unit_id": "PCR-ALPHA-01",
        "callsign": "Eagle 1 (Commercial Hub Quick Reaction)",
        "lat": 28.6298,
        "lon": 77.2170,
        "status": "PATROLLING",
        "officer": "Insp. R. Verma",
        "contact": "+91-9876543210"
    },
    {
        "unit_id": "PCR-BRAVO-04",
        "callsign": "Cheetah 4 (Sector Interceptor)",
        "lat": 28.6335,
        "lon": 77.2215,
        "status": "STANDBY",
        "officer": "SI K. Sengar",
        "contact": "+91-9876543211"
    },
    {
        "unit_id": "PCR-CHARLIE-09",
        "callsign": "Vajra 9 (Transit Station Standby)",
        "lat": 28.6350,
        "lon": 77.2155,
        "status": "STATIONARY",
        "officer": "Insp. M. Joshi",
        "contact": "+91-9876543212"
    }
]
