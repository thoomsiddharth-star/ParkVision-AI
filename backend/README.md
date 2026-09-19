# ParkVision AI — Backend API Server

> Production-ready FastAPI backend for the ParkVision AI smart parking management platform.

## Architecture

```
Camera / Demo Simulation Engine
        ↓
DetectionService (Abstract)
  ├── DemoDetectionService (demo mode)
  └── YOLODetectionService (production)
        ↓
Parking Space Status Updates
        ↓
SQLAlchemy ORM → SQLite / PostgreSQL
        ↓
Analytics / Recommendations / AI Insights
        ↓
REST API + WebSocket (/ws/parking)
        ↓
ParkVision AI Frontend (index.html)
```

## Requirements

- Python 3.10+
- pip (or uv)

## Quick Start

### 1. Create virtual environment and install dependencies

```bash
cd d:\hackathon
python -m venv .venv

# Windows
.venv\Scripts\pip install -r backend\requirements.txt

# Linux / macOS
.venv/bin/pip install -r backend/requirements.txt
```

### 2. Configure environment variables (optional)

```bash
copy backend\.env.example backend\.env
# Edit .env as needed — defaults work out of the box
```

Key variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./parkvision.db` | Database connection string |
| `AI_MODE` | `demo` | `demo` or `yolo` |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Comma-separated allowed origins |
| `SIMULATION_INTERVAL_SECONDS` | `4.0` | Demo simulation tick interval |
| `GOOGLE_MAPS_API_KEY` | *(empty)* | Optional Google Directions API key |

### 3. Start the server

```bash
cd backend
..\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

The server will:
1. Create tables automatically (SQLite by default)
2. Seed 4 parking lots, 172 spaces, 14 cameras, events, and incidents
3. Start the background demo simulation engine
4. Serve the existing frontend at `http://localhost:8000/`

### 4. Verify

| Check | URL |
|---|---|
| Frontend | http://localhost:8000/ |
| Health | http://localhost:8000/api/health |
| Swagger | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| WebSocket | `ws://localhost:8000/ws/parking` |

---

## API Endpoints

### Health
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Backend + database health check |

### Parking Lots & Spaces
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/parking/lots` | All parking lots |
| GET | `/api/parking/lots/{id}` | Lot details |
| GET | `/api/parking/lots/{id}/spaces` | Spaces in a lot |
| GET | `/api/parking/spaces/{id}` | Individual space |
| POST | `/api/parking/spaces/{id}/select` | Select available space |
| GET | `/api/parking/live` | Real-time occupancy stats |

### Cameras
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/cameras` | All cameras |
| GET | `/api/cameras/{id}` | Camera details |
| GET | `/api/cameras/{id}/status` | Camera telemetry |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analytics/occupancy` | Hourly occupancy trends |
| GET | `/api/analytics/demand` | Traffic demand levels |
| GET | `/api/analytics/peak-hours` | Peak hour analysis |
| GET | `/api/analytics/parking-duration` | Duration brackets |
| GET | `/api/analytics/ev-utilization` | EV charger utilization |

All analytics endpoints accept `?period=today|7d|30d`.

### AI & Insights
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/ai/status` | AI detection engine status |
| GET | `/api/ai/predictions` | Predicted occupancy (next 5 hrs) |
| GET | `/api/ai/insights` | Dynamic data-driven insights |
| GET | `/api/recommendations` | Scored parking recommendations |

### Driver Mode
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/driver/search` | Find best parking with preferences |

### Navigation
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/navigation` | Turn-by-turn routing |

### Incidents
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/incidents` | All incidents |
| GET | `/api/incidents/{id}` | Incident details |
| POST | `/api/incidents/{id}/review` | Mark as REVIEWED |
| POST | `/api/incidents/{id}/resolve` | Mark as RESOLVED |

### Legacy Compatibility
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/spaces` | Legacy spaces list |
| GET | `/api/locations` | Legacy locations list |
| GET | `/api/status` | Legacy status endpoint |

---

## WebSocket — Real-Time Updates

Connect to `ws://localhost:8000/ws/parking` to receive live parking bay changes.

**Message format:**
```json
{
  "type": "parking_update",
  "space_id": 12,
  "space_number": "A12",
  "previous_status": "AVAILABLE",
  "status": "OCCUPIED",
  "timestamp": "2026-09-19T12:34:56Z",
  "confidence": 96.4,
  "vehicle_type": "White Sedan",
  "lot_id": 1
}
```

**Keepalive:** Send `"ping"` to receive `"pong"`.

---

## Demo Simulation Engine

When `AI_MODE=demo`, a background async loop runs every `SIMULATION_INTERVAL_SECONDS` (default 4s):

1. Picks 1–2 random non-reserved parking spaces
2. Toggles AVAILABLE ↔ OCCUPIED
3. Creates a `ParkingEvent` record
4. Recalculates lot statistics
5. Broadcasts the change via WebSocket

This provides a realistic live demo experience for the hackathon.

---

## Database Seed Data

4 parking lots seeded with Indian city-style data:

| Lot | Capacity | Price (₹/hr) | Initial Occupancy |
|---|---|---|---|
| Central Mall Parking | 40 | ₹50 | ~70% |
| City Center Parking | 42 | ₹60 | ~81% |
| Tech Park Parking | 40 | ₹30 | ~48% |
| Metro Station Parking | 50 | ₹20 | ~70% |

Each lot includes EV, Accessible, and Reserved spaces plus CCTV cameras and seeded incidents.

---

## Future YOLO Integration

The `DetectionService` abstraction supports drop-in replacement:

```python
# app/services/detection_service.py

class DetectionService(ABC):
    def detect_vehicles(self, frame_or_source) -> List[Dict]
    def analyze_parking_spaces(self, detections, space_polygons) -> List[Dict]
    def get_detection_results(self) -> Dict

class DemoDetectionService(DetectionService):  # ← Active in demo mode
class YOLODetectionService(DetectionService):  # ← Production with ultralytics
```

To enable real CV inference:
1. Install `ultralytics` and `torch`
2. Place YOLOv8 weights (e.g. `yolov8n.pt`)
3. Set `AI_MODE=yolo` in `.env`
4. Configure camera `stream_url` fields in the database

---

## Frontend Integration

The backend serves the existing frontend at `http://localhost:8000/`.

For a separate Vite dev server, set in your frontend `.env`:
```
VITE_API_URL=http://localhost:8000
```

CORS is pre-configured for `localhost:5173`, `localhost:3000`, and `localhost:8000`.

---

## Running Tests

```bash
cd d:\hackathon
.venv\Scripts\python -m pytest backend/tests/ -v
```

30 tests covering health, parking, cameras, analytics, AI status, recommendations, driver search, navigation, and incidents.
