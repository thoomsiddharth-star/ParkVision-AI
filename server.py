"""
ParkVision AI - Local Development & Prototype Server
Serves static frontend files and provides mock REST API endpoints for future YOLO/OpenCV backend integration.

Usage:
    python server.py [port]
Default Port:
    8000 (access at http://localhost:8000)
"""

import http.server
import socketserver
import json
import os
import sys
import mimetypes

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Initial 40 parking spaces state
available_indices = {1, 3, 5, 7, 9, 13, 17, 21, 25, 29, 33, 37}
spaces_db = []
for i in range(1, 41):
    id_str = f"A{i:02d}"
    status = "AVAILABLE" if i in available_indices else "OCCUPIED"
    if i == 6:
        status = "UNCERTAIN"
    zone = (
        "Ground Floor (North)" if i <= 10 else
        "Ground Floor (East)" if i <= 20 else
        "Ground Floor (South)" if i <= 30 else
        "Ground Floor (West)"
    )
    spaces_db.append({
        "id": id_str,
        "number": i,
        "status": status,
        "zone": zone,
        "vehicleType": "SUV" if status == "OCCUPIED" and i % 2 == 0 else ("Sedan" if status == "OCCUPIED" else None),
        "confidence": 96 if status == "OCCUPIED" else (68 if status == "UNCERTAIN" else None),
        "lastUpdated": "Just now"
    })

locations_db = [
    {
        "id": "central-hub",
        "name": "Central Parking Hub",
        "address": "450 Innovation Way, Downtown",
        "distance": "2.4 km",
        "estimatedTime": "8 min",
        "totalSpaces": 40,
        "availableSpaces": 12,
        "occupiedSpaces": 28,
        "occupancyRate": 70,
        "status": "Active",
        "rate": "$4.50 / hr",
        "lat": 37.7749,
        "lng": -122.4194
    },
    {
        "id": "city-center",
        "name": "City Center Parking",
        "address": "120 Market St, Financial Plaza",
        "distance": "3.1 km",
        "estimatedTime": "11 min",
        "totalSpaces": 42,
        "availableSpaces": 8,
        "occupiedSpaces": 34,
        "occupancyRate": 81,
        "status": "High Demand",
        "rate": "$5.00 / hr",
        "lat": 37.7833,
        "lng": -122.4167
    },
    {
        "id": "tech-park",
        "name": "Tech Park Parking",
        "address": "88 Silicon Boulevard, Tech District",
        "distance": "4.7 km",
        "estimatedTime": "14 min",
        "totalSpaces": 40,
        "availableSpaces": 21,
        "occupiedSpaces": 19,
        "occupancyRate": 48,
        "status": "Plenty Available",
        "rate": "$3.50 / hr",
        "lat": 37.7892,
        "lng": -122.4014
    },
    {
        "id": "metro-plaza",
        "name": "Metro Plaza Garage",
        "address": "15 Transit Station Rd",
        "distance": "1.2 km",
        "estimatedTime": "5 min",
        "totalSpaces": 50,
        "availableSpaces": 15,
        "occupiedSpaces": 35,
        "occupancyRate": 70,
        "status": "Active",
        "rate": "$3.00 / hr",
        "lat": 37.7690,
        "lng": -122.4467
    }
]


class ParkVisionHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # API Routes
        if self.path == '/api/status':
            self.send_json_response(self.get_stats())
            return
        elif self.path == '/api/spaces':
            self.send_json_response({"spaces": spaces_db})
            return
        elif self.path == '/api/locations':
            self.send_json_response({"locations": locations_db})
            return
        elif self.path == '/api/health':
            self.send_json_response({
                "status": "healthy",
                "service": "ParkVision AI Mock Backend",
                "visionModel": "YOLOv8 Computer Vision (Simulated)",
                "mode": "DEMO MODE — Simulated real-time detection"
            })
            return

        # Serve static frontend files
        return super().do_GET()

    def send_json_response(self, data, status_code=200):
        response_bytes = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def get_stats(self):
        total = len(spaces_db)
        avail = sum(1 for s in spaces_db if s['status'] == 'AVAILABLE')
        occ = sum(1 for s in spaces_db if s['status'] == 'OCCUPIED')
        rate = round((occ / total) * 100) if total else 0
        return {
            "total": total,
            "available": avail,
            "occupied": occ,
            "occupancyRate": rate,
            "demoMode": True,
            "model": "YOLO Computer Vision",
            "cameraStatus": "Detection Active"
        }


if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), ParkVisionHandler) as httpd:
        print(f"==================================================")
        print(f"  ParkVision AI - Web & API Server Running")
        print(f"  Access website: http://localhost:{PORT}")
        print(f"  REST API:       http://localhost:{PORT}/api/status")
        print(f"  Press Ctrl+C to terminate")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down gracefully.")
