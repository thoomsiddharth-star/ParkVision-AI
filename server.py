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

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        # API Routes
        path = self.path.split('?')[0]
        if path == '/api/status':
            self.send_json_response(self.get_stats())
            return
        elif path == '/api/spaces':
            self.send_json_response({"spaces": spaces_db})
            return
        elif path == '/api/locations':
            self.send_json_response({"locations": locations_db})
            return
        elif path == '/api/health':
            self.send_json_response({
                "status": "healthy",
                "service": "ParkVision AI Mock Backend",
                "visionModel": "YOLOv8 Computer Vision (Simulated)",
                "mode": "DEMO MODE — Simulated real-time detection"
            })
            return
        elif path == '/api/admin/dashboard':
            total = len(spaces_db)
            avail = sum(1 for s in spaces_db if s['status'] == 'AVAILABLE')
            occ = sum(1 for s in spaces_db if s['status'] == 'OCCUPIED')
            self.send_json_response({
                "total_lots": 4,
                "total_spaces": total,
                "occupied_spaces": occ,
                "available_spaces": avail,
                "active_cameras": 4,
                "total_cameras": 4,
                "open_security_incidents": 2,
                "facility_status": "OPERATIONAL"
            })
            return
        elif path == '/api/admin/cameras':
            self.send_json_response([
                {"camera_number": "CAM-01", "name": "North Lot Gate Entry", "status": "Active", "cars_detected": 12, "spaces_detected": 18, "ai_confidence": 98.4},
                {"camera_number": "CAM-02", "name": "South Deck Ramp", "status": "Active", "cars_detected": 8, "spaces_detected": 10, "ai_confidence": 96.1},
                {"camera_number": "CAM-03", "name": "East Bay Wing (P1)", "status": "Active", "cars_detected": 6, "spaces_detected": 8, "ai_confidence": 95.8},
                {"camera_number": "CAM-04", "name": "VIP & EV Charging Deck", "status": "Active", "cars_detected": 2, "spaces_detected": 4, "ai_confidence": 99.2}
            ])
            return
        elif path == '/api/admin/users':
            self.send_json_response([
                {"id": 1, "email": "admin@parkvision.ai", "full_name": "ParkVision Administrator", "role": "ADMIN", "is_active": True},
                {"id": 2, "email": "user@parkvision.ai", "full_name": "Rahul Sharma", "role": "USER", "is_active": True}
            ])
            return

        # Serve static frontend files
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        path = self.path.split('?')[0]

        if path == '/api/auth/admin/login':
            email = str(payload.get('email', '')).strip().lower()
            password = str(payload.get('password', ''))
            if email == 'admin@parkvision.ai' and password == 'theasp@1234':
                self.send_json_response({
                    "access_token": "mock_admin_token_" + str(int(os.path.getmtime(__file__))),
                    "token_type": "bearer",
                    "role": "ADMIN",
                    "user": {
                        "id": 1,
                        "email": "admin@parkvision.ai",
                        "full_name": "ParkVision Administrator",
                        "role": "ADMIN",
                        "is_active": True
                    }
                })
            else:
                self.send_json_response({
                    "success": False,
                    "error": {
                        "code": "INVALID_ADMIN_CREDENTIALS",
                        "message": "Invalid administrator credentials. Access denied."
                    }
                }, status_code=401)
            return

        elif path == '/api/auth/login':
            email = str(payload.get('email', '')).strip().lower()
            password = str(payload.get('password', ''))
            if email == 'admin@parkvision.ai' and password == 'theasp@1234':
                self.send_json_response({
                    "access_token": "mock_admin_token_" + str(int(os.path.getmtime(__file__))),
                    "token_type": "bearer",
                    "role": "ADMIN",
                    "user": {"id": 1, "email": "admin@parkvision.ai", "full_name": "ParkVision Administrator", "role": "ADMIN", "is_active": True}
                })
            elif email == 'user@parkvision.ai' and password == 'user123':
                self.send_json_response({
                    "access_token": "mock_user_token_123",
                    "token_type": "bearer",
                    "role": "USER",
                    "user": {"id": 2, "email": "user@parkvision.ai", "full_name": "Rahul Sharma", "role": "USER", "is_active": True}
                })
            else:
                self.send_json_response({
                    "success": False,
                    "error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}
                }, status_code=401)
            return

        elif path == '/api/auth/register':
            email = str(payload.get('email', '')).strip().lower()
            full_name = str(payload.get('full_name', 'Driver'))
            self.send_json_response({
                "access_token": "mock_reg_token_" + str(int(os.path.getmtime(__file__))),
                "token_type": "bearer",
                "role": "USER",
                "user": {"id": 99, "email": email, "full_name": full_name, "role": "USER", "is_active": True}
            }, status_code=201)
            return

        elif path.startswith('/api/admin/spaces/'):
            # /api/admin/spaces/{id}/status?status_action=LOCK
            parts = path.split('/')
            space_id = parts[4] if len(parts) > 4 else "1"
            action = "LOCK"
            if 'status_action=' in self.path:
                action = self.path.split('status_action=')[1].split('&')[0]
            new_status = "RESERVED" if action == "LOCK" else ("UNCERTAIN" if action == "MAINTENANCE" else "AVAILABLE")
            self.send_json_response({
                "id": int(space_id) if space_id.isdigit() else 1,
                "space_number": f"A{int(space_id) if space_id.isdigit() else 1:02d}",
                "status": new_status,
                "message": f"Space status updated to {new_status}"
            })
            return

        self.send_json_response({"error": "Endpoint not found"}, status_code=404)

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
