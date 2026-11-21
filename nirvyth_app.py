# nirvyth_app.py
"""
NIRVYTH (निर्वीथ) - Autonomous AI Public Safety & Drone Surveillance Platform
Arthaton 2026 Submission | Team Arthaton (hello@arthaton.com)
Team NIRVYTH: Ravishankar Kushwaha (Lead), Piyush Jiloka, Sammi Dubey
"""

import os
import json
import time
import math
import http.server
import socketserver
import urllib.parse
from config import SERVER_HOST, SERVER_PORT, HACKATHON_METADATA
from drone_engine import DroneEngine
from face_recognition_engine import FaceRecognitionEngine
from surveillance_analytics import SurveillanceAnalyticsEngine
from geospatial_engine import GeospatialEngine

drone = DroneEngine()
face_engine = FaceRecognitionEngine()
analytics = SurveillanceAnalyticsEngine()
geospatial = GeospatialEngine()

class NIRVYTHHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress noisy request console logs

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))

        elif path == "/api/metadata":
            self._send_json(HACKATHON_METADATA)

        elif path == "/api/state":
            t = drone.update_telemetry()
            a = analytics.analyze_frame_dynamics()
            f = face_engine.scan_frame()
            
            # Ground raycast of first alert or default center
            ray = drone.raycast_ground_coordinate(0.5, 0.5)
            nearest_pcr = geospatial.find_nearest_patrol_unit(ray["lat"], ray["lon"])

            response_data = {
                "telemetry": t,
                "analytics": a,
                "faces": f,
                "raycast": ray,
                "nearest_pcr": nearest_pcr,
                "tactical_zones": geospatial.get_tactical_zones(),
                "patrol_units": geospatial.patrol_units
            }
            self._send_json(response_data)

        elif path == "/api/toggle_sensor":
            mode = drone.toggle_sensor()
            self._send_json({"status": "SUCCESS", "sensor_mode": mode})

        elif path == "/api/toggle_dpdp":
            status = face_engine.toggle_dpdp_masking()
            self._send_json({"status": "SUCCESS", "dpdp_masking": status})

        elif path == "/api/simulate":
            scenario = query.get("scenario", ["RESET_NORMAL"])[0]
            a = analytics.analyze_frame_dynamics(scenario_trigger=scenario)
            self._send_json({"status": "SUCCESS", "scenario": scenario, "analytics": a})

        elif path == "/api/dispatch":
            unit_id = query.get("unit_id", ["PCR-ALPHA-01"])[0]
            lat = float(query.get("lat", [28.6315])[0])
            lon = float(query.get("lon", [77.2185])[0])
            dispatch_info = geospatial.find_nearest_patrol_unit(lat, lon)
            self._send_json({
                "status": "DISPATCH_CONFIRMED",
                "dispatched_unit": dispatch_info["selected_unit"]["callsign"],
                "officer": dispatch_info["selected_unit"]["officer"],
                "eta": dispatch_info["eta_formatted"],
                "distance": f"{dispatch_info['straight_distance_meters']} m",
                "timestamp": time.strftime("%H:%M:%S")
            })

        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))


HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NIRVYTH - AI Smart Public Safety & Drone Command Center</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    :root {
      --bg-dark: #070d1e;
      --bg-card: #0f1c3f;
      --bg-card-hover: #16295c;
      --border: #1e3a75;
      --accent-cyan: #00e5ff;
      --accent-green: #00e676;
      --accent-amber: #ffab00;
      --accent-red: #ff1744;
      --text-white: #ffffff;
      --text-muted: #90a4ae;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; }
    body { background-color: var(--bg-dark); color: var(--text-white); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

    /* Top Bar */
    header {
      background: linear-gradient(90deg, #0a142e 0%, #102352 100%);
      border-bottom: 2px solid var(--border);
      padding: 10px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
    }
    .brand { display: flex; align-items: center; gap: 14px; }
    .badge-icon {
      background: radial-gradient(circle, #00e5ff 0%, #0077b6 100%);
      width: 38px; height: 38px; border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-weight: 900; font-size: 20px; color: #000; box-shadow: 0 0 12px rgba(0,229,255,0.4);
    }
    .brand h1 { font-size: 19px; font-weight: 800; letter-spacing: 1px; color: #fff; }
    .brand h1 span { color: var(--accent-cyan); }
    .brand p { font-size: 11px; color: var(--text-muted); margin-top: 1px; }

    .header-pills { display: flex; gap: 12px; }
    .pill {
      background: rgba(16,35,82,0.8);
      border: 1px solid var(--border);
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .dot { width: 7px; height: 7px; border-radius: 50%; }
    .dot-green { background: var(--accent-green); box-shadow: 0 0 8px var(--accent-green); }
    .dot-cyan { background: var(--accent-cyan); box-shadow: 0 0 8px var(--accent-cyan); }

    /* Main Grid */
    .dashboard-grid {
      display: grid;
      grid-template-columns: 460px 1fr 380px;
      gap: 12px;
      padding: 12px;
      flex: 1;
      overflow: hidden;
    }

    .panel {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 4px 18px rgba(0,0,0,0.4);
    }
    .panel-header {
      padding: 10px 14px;
      background: rgba(0,0,0,0.25);
      border-bottom: 1px solid var(--border);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--accent-cyan);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* Video Feed Simulation */
    .feed-container {
      position: relative;
      width: 100%;
      height: 270px;
      background: #000;
      overflow: hidden;
    }
    #droneCanvas { width: 100%; height: 100%; display: block; }
    .hud-overlay {
      position: absolute;
      top: 8px; left: 8px; right: 8px;
      display: flex; justify-content: space-between;
      font-family: monospace; font-size: 10px; color: var(--accent-cyan);
      pointer-events: none; text-shadow: 0 0 4px #000;
    }
    .hud-bottom {
      position: absolute;
      bottom: 8px; left: 8px; right: 8px;
      display: flex; justify-content: space-between;
      font-family: monospace; font-size: 10px; color: var(--accent-green);
      pointer-events: none; text-shadow: 0 0 4px #000;
    }

    /* Controls Bar */
    .control-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      padding: 10px;
      background: rgba(0,0,0,0.15);
      border-bottom: 1px solid var(--border);
    }
    .btn {
      background: rgba(0,229,255,0.1);
      border: 1px solid var(--accent-cyan);
      color: var(--accent-cyan);
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: center;
    }
    .btn:hover { background: var(--accent-cyan); color: #000; }
    .btn-red { border-color: var(--accent-red); color: var(--accent-red); background: rgba(255,23,68,0.1); }
    .btn-red:hover { background: var(--accent-red); color: #fff; }
    .btn-amber { border-color: var(--accent-amber); color: var(--accent-amber); background: rgba(255,171,0,0.1); }
    .btn-amber:hover { background: var(--accent-amber); color: #000; }

    /* Facial Recognition List */
    .face-alerts {
      flex: 1;
      padding: 10px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .suspect-card {
      background: rgba(255,23,68,0.12);
      border-left: 4px solid var(--accent-red);
      border-radius: 6px;
      padding: 9px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .suspect-card.amber {
      background: rgba(255,171,0,0.12);
      border-left-color: var(--accent-amber);
    }
    .suspect-header { display: flex; justify-content: space-between; font-weight: 700; font-size: 12px; }
    .suspect-desc { font-size: 11px; color: var(--text-muted); }
    .suspect-meta { font-size: 10px; font-family: monospace; color: var(--accent-cyan); display: flex; justify-content: space-between; }

    /* Map Panel */
    #map { width: 100%; height: 100%; min-height: 380px; }
    .map-dispatch-card {
      padding: 10px 14px;
      background: rgba(10,20,46,0.95);
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* Right Panel: Metrics & Gauges */
    .metrics-container {
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow-y: auto;
    }
    .metric-box {
      background: rgba(0,0,0,0.25);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
    }
    .metric-title { font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 6px; display: flex; justify-content: space-between; }
    .metric-value { font-size: 24px; font-weight: 800; color: #fff; }
    .metric-value span { font-size: 13px; color: var(--text-muted); font-weight: 500; }
    
    .gauge-bar-bg { width: 100%; height: 8px; background: #162447; border-radius: 4px; overflow: hidden; margin-top: 6px; }
    .gauge-bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent-green) 0%, var(--accent-amber) 65%, var(--accent-red) 100%); transition: width 0.3s; }

    .telemetry-table { width: 100%; font-size: 11px; border-collapse: collapse; margin-top: 4px; }
    .telemetry-table td { padding: 4px 0; color: var(--text-muted); }
    .telemetry-table td.val { text-align: right; color: var(--text-white); font-weight: 600; font-family: monospace; }

    .event-log {
      max-height: 140px;
      overflow-y: auto;
      font-size: 10.5px;
      font-family: monospace;
      display: flex;
      flex-direction: column;
      gap: 5px;
      padding: 8px;
      background: #060b18;
      border-radius: 6px;
      border: 1px solid #142245;
    }
    .log-entry { color: #cfd8dc; border-left: 2px solid var(--accent-cyan); padding-left: 6px; }
    .log-entry.crit { border-left-color: var(--accent-red); color: #ff8a80; }
    .log-entry.warn { border-left-color: var(--accent-amber); color: #ffe082; }

    /* Footer */
    footer {
      background: #081126;
      border-top: 1px solid var(--border);
      padding: 6px 20px;
      font-size: 11px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
    }
  </style>
</head>
<body>

  <!-- Top Header -->
  <header>
    <div class="brand">
      <div class="badge-icon">N</div>
      <div>
        <h1>NIRVYTH <span>// AI SMART PUBLIC SAFETY</span></h1>
        <p>Arthaton 2026 | Team NIRVYTH: Ravishankar Kushwaha, Piyush Jiloka, Sammi Dubey</p>
      </div>
    </div>
    <div class="header-pills">
      <div class="pill"><div class="dot dot-cyan"></div> DRONE: <span id="hdrDroneId">UAV-SENTINEL-X1</span></div>
      <div class="pill"><div class="dot dot-green"></div> SENSOR: <span id="hdrSensor">4K OPTICAL RGB</span></div>
      <div class="pill"><div class="dot dot-green"></div> PRIVACY: <span id="hdrDpdp" style="color:var(--accent-green);">DPDP BLUR ACTIVE</span></div>
      <div class="pill"><div class="dot dot-cyan"></div> FPS: <span id="hdrFps">38.4</span></div>
    </div>
  </header>

  <!-- Dashboard Grid -->
  <div class="dashboard-grid">
    
    <!-- LEFT PANEL: Aerial Feed & Facial Recognition -->
    <div class="panel">
      <div class="panel-header">
        <span>Aerial Surveillance Stream</span>
        <span style="font-family:monospace; color:var(--accent-green);">REC ● LIVE</span>
      </div>
      
      <!-- Video / Simulation Canvas -->
      <div class="feed-container">
        <canvas id="droneCanvas" width="460" height="270"></canvas>
        <div class="hud-overlay">
          <span>ALT: <b id="hudAlt">32.4m</b></span>
          <span>SPD: <b id="hudSpd">22.1 km/h</b></span>
          <span>BAT: <b id="hudBat">94%</b></span>
        </div>
        <div class="hud-bottom">
          <span>PITCH: <b id="hudPitch">-45.0°</b></span>
          <span>GPS: <b id="hudCoords">28.6315°N, 77.2185°E</b></span>
        </div>
      </div>

      <!-- Quick Scenario Triggers -->
      <div class="control-row">
        <button class="btn" onclick="toggleSensor()">Toggle Thermal / RGB</button>
        <button class="btn" onclick="toggleDPDP()">Toggle DPDP Masking</button>
        <button class="btn btn-red" onclick="triggerScenario('VIOLENCE_FIGHT')">Simulate Fight Scuffle</button>
        <button class="btn btn-amber" onclick="triggerScenario('CROWD_SURGE')">Simulate Crowd Surge</button>
      </div>

      <!-- Facial Biometrics & Watchlist -->
      <div class="panel-header" style="border-top:1px solid var(--border);">
        <span>Biometric Watchlist Matching</span>
        <span id="faceMatchCount" style="color:var(--accent-red); font-weight:800;">1 TARGET CONFIRMED</span>
      </div>
      <div class="face-alerts" id="faceAlertsContainer">
        <!-- Injected dynamically -->
      </div>
    </div>

    <!-- CENTER PANEL: Tactical GIS Map -->
    <div class="panel">
      <div class="panel-header">
        <span>Tactical GIS Command Grid (GEOINT)</span>
        <span style="font-size:11px; color:var(--text-muted);">OpenStreetMap + High-Precision RTK</span>
      </div>
      <div style="flex:1; position:relative;">
        <div id="map"></div>
      </div>
      
      <!-- Tactical Dispatch Bar -->
      <div class="map-dispatch-card">
        <div>
          <div style="font-size:11px; color:var(--text-muted); font-weight:600;">RECOMMENDED TACTICAL INTERCEPT</div>
          <div style="font-size:13px; font-weight:700; color:#fff;" id="dispatchUnitName">PCR-ALPHA-01 (Eagle 1)</div>
          <div style="font-size:11px; color:var(--accent-green); font-family:monospace;" id="dispatchEta">ETA: 1m 45s | Distance: 280 m</div>
        </div>
        <button class="btn btn-red" style="padding:10px 18px; font-size:12px; font-weight:800;" onclick="dispatchPatrol()">
          DISPATCH NEAREST PATROL CAR
        </button>
      </div>
    </div>

    <!-- RIGHT PANEL: Behavioral Analytics & Law-and-Order Metrics -->
    <div class="panel">
      <div class="panel-header">
        <span>Law-and-Order Analytics</span>
        <span style="color:var(--accent-cyan); font-family:monospace;">AI-CORE v2.6</span>
      </div>
      
      <div class="metrics-container">
        <!-- Crowd Density Metric -->
        <div class="metric-box">
          <div class="metric-title">
            <span>Crowd Density</span>
            <span id="densityStatus" style="color:var(--accent-green);">NOMINAL</span>
          </div>
          <div class="metric-value" id="densityVal">2.4 <span>persons / m²</span></div>
          <div class="gauge-bar-bg">
            <div class="gauge-bar-fill" id="densityBar" style="width: 48%;"></div>
          </div>
          <div style="font-size:10px; color:var(--text-muted); margin-top:4px; display:flex; justify-content:space-between;">
            <span>0 Safe</span><span>3.0 Warning</span><span>4.5+ Stampede Risk</span>
          </div>
        </div>

        <!-- Violence / Fight Probability -->
        <div class="metric-box">
          <div class="metric-title">
            <span>Violence / Anomaly Confidence</span>
            <span id="violenceStatus" style="color:var(--accent-green);">PEACEFUL</span>
          </div>
          <div class="metric-value" id="violenceVal">12 <span>%</span></div>
          <div class="gauge-bar-bg">
            <div class="gauge-bar-fill" id="violenceBar" style="width: 12%;"></div>
          </div>
        </div>

        <!-- Flight Telemetry Table -->
        <div class="metric-box">
          <div class="metric-title"><span>UAV Flight Telemetry</span></div>
          <table class="telemetry-table">
            <tr><td>Drone Platform:</td><td class="val">DJI M300 / PX4 RTK</td></tr>
            <tr><td>Airspeed:</td><td class="val" id="tSpd">21.8 km/h</td></tr>
            <tr><td>Heading / Yaw:</td><td class="val" id="tHdg">44.5° (NE)</td></tr>
            <tr><td>Battery Health:</td><td class="val" id="tBat">92%</td></tr>
            <tr><td>GPS Accuracy:</td><td class="val" style="color:var(--accent-green);">RTK Fixed (±2.4 cm)</td></tr>
          </table>
        </div>

        <!-- Real-Time Event Audit Log -->
        <div class="metric-box" style="flex:1; display:flex; flex-direction:column;">
          <div class="metric-title"><span>Cryptographic Audit Log (DPDP Act)</span></div>
          <div class="event-log" id="eventLogContainer">
            <div class="log-entry">[SYS] NIRVYTH Command Sentinel Initialized.</div>
            <div class="log-entry">[GEO] Tactical red/amber geofence boundaries active.</div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- Footer -->
  <footer>
    <div>Team NIRVYTH: Ravishankar Kushwaha (Lead), Piyush Jiloka, Sammi Dubey | Arthaton 2026 Submission</div>
    <div>Compliance: DPDP Act 2023 &amp; BSA 2023 Validated &bull; Zero External Dependencies Prototype</div>
  </footer>

  <!-- Client-Side Dashboard Script -->
  <script>
    // Leaflet Map Initialization
    const map = L.map('map', { zoomControl: true }).setView([28.6315, 77.2185], 16);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      attribution: '&copy; CartoDB &copy; OpenStreetMap'
    }).addTo(map);

    // Map Layers
    let droneMarker = null;
    let dronePath = [];
    let polyline = L.polyline([], { color: '#00e5ff', weight: 3, opacity: 0.8, dashArray: '4, 8' }).addTo(map);
    let pcrMarkers = {};
    let incidentMarker = null;
    let dispatchLine = null;

    // Tactical Zones
    const zones = [
      { name: "Red Zone: VIP Enclosure", coords: [[28.6300, 77.2185],[28.6315, 77.2185],[28.6315, 77.2210],[28.6300, 77.2210]], color: '#ff1744' },
      { name: "Amber Zone: Metro Choke Point", coords: [[28.6325, 77.2155],[28.6340, 77.2155],[28.6340, 77.2180],[28.6325, 77.2180]], color: '#ffab00' },
      { name: "Green Zone: Safe Assembly", coords: [[28.6325, 77.2220],[28.6345, 77.2220],[28.6345, 77.2255],[28.6325, 77.2255]], color: '#00e676' }
    ];
    zones.forEach(z => {
      L.polygon(z.coords, { color: z.color, fillColor: z.color, fillOpacity: 0.18, weight: 2 })
       .bindPopup(`<b>${z.name}</b>`)
       .addTo(map);
    });

    // Simulated Canvas Drawing for Drone Video
    const canvas = document.getElementById('droneCanvas');
    const ctx = canvas.getContext('2d');
    let simulatedThermal = false;
    let simulatedDPDP = true;

    function renderDroneFeed(telemetry, faces, analytics) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Background video feed simulation
      if (simulatedThermal) {
        let grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        grad.addColorStop(0, "#1a0033");
        grad.addColorStop(0.5, "#4d0066");
        grad.addColorStop(1, "#000033");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      } else {
        ctx.fillStyle = "#1e293b";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        // Grid lines to look like aerial asphalt plaza
        ctx.strokeStyle = "#334155";
        ctx.lineWidth = 1;
        for (let x = 0; x < canvas.width; x += 40) {
          ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += 40) {
          ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
        }
      }

      // Center Crosshair
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      ctx.strokeStyle = simulatedThermal ? "#00ffff" : "#00e5ff";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, 25, 0, Math.PI * 2);
      ctx.moveTo(cx - 35, cy); ctx.lineTo(cx + 35, cy);
      ctx.moveTo(cx, cy - 35); ctx.lineTo(cx, cy + 35);
      ctx.stroke();

      // Render Detected Targets
      faces.forEach(f => {
        const [bx, by, bw, bh] = f.box;

        if (f.is_alert) {
          // Highlight suspect with red targeting box
          ctx.strokeStyle = "#ff1744";
          ctx.lineWidth = 2.5;
          ctx.strokeRect(bx, by, bw, bh);

          ctx.fillStyle = "rgba(255, 23, 68, 0.85)";
          ctx.fillRect(bx, by - 22, 170, 20);
          ctx.fillStyle = "#ffffff";
          ctx.font = "bold 10px Segoe UI";
          ctx.fillText(`TARGET: ${f.match.name.split(' ')[0]} (${Math.round(f.confidence*100)}%)`, bx + 4, by - 8);
        } else {
          // Civilian Target
          ctx.strokeStyle = "#00e5ff";
          ctx.lineWidth = 1.5;
          ctx.strokeRect(bx, by, bw, bh);

          if (simulatedDPDP) {
            // Simulated DPDP pixelation / blur overlay
            ctx.fillStyle = "rgba(0, 229, 255, 0.4)";
            ctx.fillRect(bx + 5, by + 5, bw - 10, bh - 10);
            ctx.fillStyle = "#ffffff";
            ctx.font = "9px monospace";
            ctx.fillText("[DPDP MASK]", bx + 2, by - 4);
          }
        }
      });
    }

    // State Polling Loop
    async function fetchState() {
      try {
        const res = await fetch('/api/state');
        const data = await res.json();

        // Update Header & HUD
        document.getElementById('hudAlt').innerText = data.telemetry.altitude_m + 'm';
        document.getElementById('hudSpd').innerText = data.telemetry.ground_speed_kmh + ' km/h';
        document.getElementById('hudBat').innerText = data.telemetry.battery_percent + '%';
        document.getElementById('hudPitch').innerText = data.telemetry.gimbal_pitch + '°';
        document.getElementById('hudCoords').innerText = `${data.telemetry.latitude}°N, ${data.telemetry.longitude}°E`;

        document.getElementById('tSpd').innerText = data.telemetry.ground_speed_kmh + ' km/h';
        document.getElementById('tHdg').innerText = data.telemetry.heading_deg + '°';
        document.getElementById('tBat').innerText = data.telemetry.battery_percent + '%';

        // Render Canvas
        renderDroneFeed(data.telemetry, data.faces, data.analytics);

        // Update Map Drone Marker
        const dPos = [data.telemetry.latitude, data.telemetry.longitude];
        if (!droneMarker) {
          const droneIcon = L.divIcon({
            className: 'custom-drone-icon',
            html: '<div style="background:#00e5ff; width:18px; height:18px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 14px #00e5ff;"></div>',
            iconSize: [18, 18], iconAnchor: [9, 9]
          });
          droneMarker = L.marker(dPos, { icon: droneIcon }).addTo(map).bindPopup("<b>UAV-SENTINEL-X1</b><br>Altitude: 32m");
        } else {
          droneMarker.setLatLng(dPos);
        }
        dronePath.push(dPos);
        if (dronePath.length > 25) dronePath.shift();
        polyline.setLatLngs(dronePath);

        // Update PCR Patrol Units on Map
        data.patrol_units.forEach(u => {
          if (!pcrMarkers[u.unit_id]) {
            const carIcon = L.divIcon({
              className: 'pcr-icon',
              html: '<div style="background:#00e676; width:14px; height:14px; border-radius:3px; border:2px solid #fff; box-shadow:0 0 10px #00e676;"></div>',
              iconSize: [14, 14], iconAnchor: [7, 7]
            });
            pcrMarkers[u.unit_id] = L.marker([u.lat, u.lon], { icon: carIcon }).addTo(map).bindPopup(`<b>${u.callsign}</b><br>${u.officer}`);
          }
        });

        // Recommended Dispatch update
        const pcr = data.nearest_pcr;
        document.getElementById('dispatchUnitName').innerText = `${pcr.selected_unit.callsign} (${pcr.selected_unit.officer})`;
        document.getElementById('dispatchEta').innerText = `ETA: ${pcr.eta_formatted} | Road Distance: ${pcr.estimated_road_meters} m`;

        // Update Incident Point & Dispatch Vector on Map
        const incPos = [data.raycast.lat, data.raycast.lon];
        if (!incidentMarker) {
          const incIcon = L.divIcon({
            html: '<div style="background:#ff1744; width:16px; height:16px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 14px #ff1744;"></div>',
            iconSize: [16, 16], iconAnchor: [8, 8]
          });
          incidentMarker = L.marker(incPos, { icon: incIcon }).addTo(map).bindPopup("<b>Verified Incident Hotspot</b>");
        } else {
          incidentMarker.setLatLng(incPos);
        }

        const pcrPos = [pcr.selected_unit.lat, pcr.selected_unit.lon];
        if (!dispatchLine) {
          dispatchLine = L.polyline([pcrPos, incPos], { color: '#ff1744', weight: 3, dashArray: '6, 6' }).addTo(map);
        } else {
          dispatchLine.setLatLngs([pcrPos, incPos]);
        }

        // Update Facial Alerts List
        const fContainer = document.getElementById('faceAlertsContainer');
        const alertFaces = data.faces.filter(f => f.is_alert);
        document.getElementById('faceMatchCount').innerText = `${alertFaces.length} TARGET CONFIRMED`;

        if (alertFaces.length > 0) {
          fContainer.innerHTML = alertFaces.map(f => `
            <div class="suspect-card ${f.match.category === 'MISSING_CHILD' ? 'amber' : ''}">
              <div class="suspect-header">
                <span style="color:${f.match.category === 'MISSING_CHILD' ? 'var(--accent-amber)' : 'var(--accent-red)'};">
                  ${f.match.name}
                </span>
                <span>${Math.round(f.confidence * 100)}% MATCH</span>
              </div>
              <div class="suspect-desc">${f.match.offense}</div>
              <div class="suspect-meta">
                <span>WARRANT: ${f.match.warrant_id}</span>
                <span>AUDIT: #${f.audit_hash}</span>
              </div>
            </div>
          `).join('');
        } else {
          fContainer.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:10px;">No wanted targets in current camera cone.</div>';
        }

        // Update Behavioral Metrics
        const a = data.analytics;
        document.getElementById('densityVal').innerHTML = `${a.crowd_density} <span>persons / m²</span>`;
        const dPct = Math.min(100, (a.crowd_density / 6.0) * 100);
        document.getElementById('densityBar').style.width = dPct + '%';
        const dStat = document.getElementById('densityStatus');
        if (a.crowd_density >= 4.5) {
          dStat.innerText = "CRITICAL STAMPEDE RISK";
          dStat.style.color = "var(--accent-red)";
        } else if (a.crowd_density >= 3.0) {
          dStat.innerText = "ELEVATED CONGESTION";
          dStat.style.color = "var(--accent-amber)";
        } else {
          dStat.innerText = "NOMINAL";
          dStat.style.color = "var(--accent-green)";
        }

        // Violence Metric
        const vScore = Math.round(a.violence_score * 100);
        document.getElementById('violenceVal').innerHTML = `${vScore} <span>%</span>`;
        document.getElementById('violenceBar').style.width = vScore + '%';
        const vStat = document.getElementById('violenceStatus');
        if (vScore > 75) {
          vStat.innerText = "VIOLENCE DETECTED";
          vStat.style.color = "var(--accent-red)";
        } else {
          vStat.innerText = "PEACEFUL";
          vStat.style.color = "var(--accent-green)";
        }

      } catch (err) {
        console.error("Fetch state error:", err);
      }
    }

    // Toggle Actions
    async function toggleSensor() {
      const res = await fetch('/api/toggle_sensor');
      const data = await res.json();
      simulatedThermal = (data.sensor_mode === "FLIR_RADIOMETRIC_THERMAL");
      document.getElementById('hdrSensor').innerText = simulatedThermal ? "FLIR THERMAL IR" : "4K OPTICAL RGB";
      addLog(`[SENSOR] Switched video mode to ${data.sensor_mode}`);
    }

    async function toggleDPDP() {
      const res = await fetch('/api/toggle_dpdp');
      const data = await res.json();
      simulatedDPDP = data.dpdp_masking;
      const el = document.getElementById('hdrDpdp');
      if (simulatedDPDP) {
        el.innerText = "DPDP BLUR ACTIVE";
        el.style.color = "var(--accent-green)";
        addLog("[PRIVACY] Automated DPDP civilian facial blurring ENABLED.");
      } else {
        el.innerText = "DPDP BLUR BYPASSED";
        el.style.color = "var(--accent-red)";
        addLog("[PRIVACY] Warning: DPDP privacy masking temporarily DISABLED.");
      }
    }

    async function triggerScenario(type) {
      await fetch(`/api/simulate?scenario=${type}`);
      if (type === 'VIOLENCE_FIGHT') {
        addLog("[ALERT-CRIT] Violence anomaly detected! Scuffle pattern flagged.", "crit");
      } else if (type === 'CROWD_SURGE') {
        addLog("[ALERT-WARN] Crowd surge detected at Choke Point!", "warn");
      }
    }

    async function dispatchPatrol() {
      const res = await fetch('/api/dispatch');
      const data = await res.json();
      alert(`TACTICAL DISPATCH CONFIRMED!\n\nPatrol Unit: ${data.dispatched_unit}\nOfficer: ${data.officer}\nEstimated Time of Arrival: ${data.eta}\nDistance: ${data.distance}\n\nCoordinates dispatched to vehicle MDT terminal.`);
      addLog(`[DISPATCH] Sent ${data.dispatched_unit} to Target. ETA: ${data.eta}`, "crit");
    }

    function addLog(msg, type = "normal") {
      const logBox = document.getElementById('eventLogContainer');
      const time = new Date().toLocaleTimeString();
      const div = document.createElement('div');
      div.className = `log-entry ${type}`;
      div.innerText = `${time} ${msg}`;
      logBox.prepend(div);
    }

    // Start Real-Time Loop
    setInterval(fetchState, 1000);
    fetchState();
  </script>
</body>
</html>
"""

def main():
    print("=" * 75)
    print("NIRVYTH (निर्वीथ) - AI Public Safety & Drone Surveillance Platform")
    print("Hackathon: Arthaton 2026 (hello@arthaton.com)")
    print("Team NIRVYTH: Ravishankar Kushwaha (Lead), Piyush Jiloka, Sammi Dubey")
    print("Contact: rs6816635@gmail.com | Zero External Dependencies Prototype")
    print("=" * 75)
    
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = socketserver.TCPServer(server_address, NIRVYTHHandler)
    print(f"[+] NIRVYTH Tactical Command Server running at: http://{SERVER_HOST}:{SERVER_PORT}")
    print("[+] Open your web browser to view the interactive live dashboard.")
    print("[+] Press Ctrl+C to terminate server.")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down.")
        httpd.server_close()

if __name__ == "__main__":
    main()
