# ParkVision AI — Smart Parking Management Platform

> **Core Promise Statement (Verbatim):**  
> *“Develop a camera-based solution that detects available and occupied parking spaces in real time and provides users with parking availability and navigation information.”*

ParkVision AI is a smart parking solution that uses camera-based computer vision to detect available and occupied parking spaces in real time. It presents the parking status through a web interface and provides users with parking availability information and navigation to the parking area.

---

## 🌟 Key Features

1. **Landing Page**:
   - High-impact "AI + Smart City" hero design with live mini-lot visualization.
   - Verbatim Promise Statement card.
   - 5-Step visual pipeline: Camera → AI Detection → Space Analysis → Real-Time Update → Navigation.

2. **Live Parking Status Dashboard**:
   - Monitored bays (A01 to A40) with color-coded status badges (Green = AVAILABLE, Red = OCCUPIED, Amber = UNCERTAIN).
   - Real-time KPI metrics: Total Spaces (40), Available (12), Occupied (28), Occupancy (70%), dynamic timestamps.
   - Interactive bay selection with status warning modal for occupied slots and one-click filtering.

3. **AI Detection & Computer Vision Simulation**:
   - Interactive HTML5 Canvas CCTV stream with asphalt bay markings, parked vehicles, and live YOLO bounding boxes (`A01 → AVAILABLE`, `A02 → OCCUPIED [96%]`).
   - Radar scanline and camera HUD telemetry (30 FPS, 14ms latency, RTSP stream label).
   - Camera switching between North Lot and South Deck.
   - **Honest Disclosure**: Prominently labeled with `“DEMO MODE — Simulated real-time detection”` and `“AI Detection Demo”`.

4. **Find Parking & Nearby Locations**:
   - Facility cards for *Central Parking Hub*, *City Center Parking*, *Tech Park Parking*, and *Metro Plaza Garage*.
   - Live distance, estimated travel time, real-time rates, and occupancy percentages.

5. **Parking Details & Space Selection**:
   - Interactive ground floor layout allowing drivers to reserve an available bay (e.g. `Space A12 selected`).
   - Direct handoff to navigation.

6. **Navigation Experience**:
   - Map-style route preview with GPS pathing mockup.
   - Distance (2.4 km), Travel Time (8 min), Available spaces (12).
   - Direct link to launch Google Maps with pre-filled destination coordinates.

7. **Operator Dashboard**:
   - Executive KPIs: Peak Occupancy, Average Occupancy, Utilization, Turnover rate.
   - Charts (via Chart.js): Hourly Occupancy trend, Zone capacity breakdown, Live rolling availability stream.
   - Live activity stream of vehicle arrivals and departures.

8. **Admin Operations Portal (`admin-dashboard.html`)**:
   - Dedicated administrative suite with **three top navigating headsets**:
     1. **📐 Headset 1: Floor Plan & Coverage Boundary**: Insert custom floor plan blueprints or templates and define the *exact area the camera should cover* — covering not more and not less than that.
     2. **📹 Headset 2: Live Camera Output (Traffic-Adaptive 10–30s Scan)**: Real-time CCTV feed with YOLOv8 vehicle detections, live countdown timer, and adaptive scan intervals dynamically varying between 10s and 30s based on vehicle traffic.
     3. **📊 Headset 3: Traffic & Space Management**: Facility KPIs, bay status overrides (Lock, Free, Block), and live vehicle arrival/departure audit logs.
   - Bidirectional navigation: Prominent `← Back to User Panel` button and quick-switch sub-bar to transition between admin and driver portals at any time.

9. **Dedicated Admin Login (`admin-login.html`)**:
   - Standalone login portal for authorized personnel.
   - Credentials: `admin@parkvision.ai` / `theasp@1234`.
   - Automatic credential recognition from the user login modal with instant redirection.

---

## 🚀 Quick Start

You can run ParkVision AI either by directly opening `index.html` in any modern web browser or by launching the included lightweight Python server.

### Option 1: Run with Python Server (Recommended)
```bash
# In the project directory:
python server.py
```
Then open your browser and navigate to:
```
http://localhost:8000
```

### Option 2: Direct Browser Launch
Simply double click or open `index.html` in your browser:
```bash
start index.html
```

---

## 🏛️ System Architecture

```
+------------------+       +-------------------+       +-----------------------+
|  CCTV IP Camera  | ----> |  OpenCV & PyTorch | ----> |  Ultralytics YOLOv8   |
|  (RTSP 1080p)    |       |  Frame Capture    |       |  Vehicle & Bay Detect |
+------------------+       +-------------------+       +-----------------------+
                                                                   |
                                                                   v
+------------------+       +-------------------+       +-----------------------+
|   Web UI SPA     | <---- |   FastAPI / REST  | <---- |  Real-Time Database   |
|  (ParkVision AI) |       |  WebSocket Feeds  |       |  (PostgreSQL/Firebase)|
+------------------+       +-------------------+       +-----------------------+
```

### Future Production Backend Stack:
- **Computer Vision**: OpenCV, Ultralytics YOLOv8 / YOLOv11 for multi-class vehicle detection.
- **Backend API**: Python FastAPI or Flask with WebSocket pub/sub for real-time bay state broadcasts.
- **Database**: PostgreSQL (with PostGIS for geospatial indexing) or Firebase Realtime DB.
- **Hardware**: Edge devices (NVIDIA Jetson / Raspberry Pi 5) or cloud GPU inference nodes.

---

## 🎤 Hackathon Demonstration Script

1. **Hero & Landing**: Showcase the hero headline and live mini-lot bays switching states in real time.
2. **5-Step Flow**: Walk judges through the 5-step visual pipeline.
3. **Live Parking Screen**: Point out the 40 parking bays (A01-A40). Click an occupied space to demonstrate the warning and available space suggestion. Click an available space to show confirmation.
4. **AI Detection Screen**: Demonstrate the computer vision CCTV feed with bounding boxes, confidence tags, and camera switching. Emphasize the honest `DEMO MODE` label.
5. **Find Parking & Navigation**: Select *Central Parking Hub*, pick a bay, click *Start Navigation*, and show the route preview with Google Maps handoff.
6. **Dashboard**: Show operator analytics with Chart.js hourly trends and zone breakdowns.
