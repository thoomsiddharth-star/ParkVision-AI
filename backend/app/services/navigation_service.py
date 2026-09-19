import math
from typing import Dict, Any, List
from app.services.recommendation_service import haversine_distance_km
from app.core.config import settings
import httpx

class NavigationService:
    @staticmethod
    async def get_route(
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        destination_name: str = "Central Mall Parking"
    ) -> Dict[str, Any]:
        """
        Provides turn-by-turn routing between origin and destination coordinates.
        Uses Google Directions API if GOOGLE_MAPS_API_KEY is configured;
        otherwise provides a high-fidelity simulated route for hackathon demo.
        """
        if settings.GOOGLE_MAPS_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(
                        "https://maps.googleapis.com/maps/api/directions/json",
                        params={
                            "origin": f"{origin_lat},{origin_lng}",
                            "destination": f"{dest_lat},{dest_lng}",
                            "key": settings.GOOGLE_MAPS_API_KEY
                        }
                    )
                    data = resp.json()
                    if data.get("status") == "OK" and data.get("routes"):
                        route = data["routes"][0]
                        leg = route["legs"][0]
                        steps = [
                            {
                                "instruction": step.get("html_instructions", "").replace("<b>", "").replace("</b>", ""),
                                "distance": step.get("distance", {}).get("text", ""),
                                "duration": step.get("duration", {}).get("text", "")
                            }
                            for step in leg.get("steps", [])
                        ]
                        return {
                            "origin": {"lat": origin_lat, "lng": origin_lng},
                            "destination_coords": {"lat": dest_lat, "lng": dest_lng},
                            "destination_name": destination_name,
                            "distance": leg.get("distance", {}).get("text", "2.4 km"),
                            "distance_km": round(leg.get("distance", {}).get("value", 2400) / 1000.0, 2),
                            "estimated_time": leg.get("duration", {}).get("text", "8 min"),
                            "duration_minutes": round(leg.get("duration", {}).get("value", 480) / 60),
                            "route_provider": "Google Maps Directions API",
                            "polyline": [
                                {"lat": step.get("start_location", {}).get("lat", origin_lat),
                                 "lng": step.get("start_location", {}).get("lng", origin_lng)}
                                for step in leg.get("steps", [])
                            ],
                            "steps": steps
                        }
            except Exception as e:
                # Fall through to simulated route on network/API failure
                pass

        # Demo Route Simulation (clearly disclosed)
        dist_km = haversine_distance_km(origin_lat, origin_lng, dest_lat, dest_lng)
        if dist_km < 0.1:
            dist_km = 2.4  # Default realistic demo distance

        # Assuming average city driving speed of 22 km/h with traffic
        duration_mins = max(2, int((dist_km / 22.0) * 60))

        # Generate smooth intermediate route coordinates
        num_waypoints = 5
        polyline = []
        for i in range(num_waypoints + 1):
            ratio = i / float(num_waypoints)
            # Add slight curvature for realism
            lat_jitter = math.sin(ratio * math.pi) * 0.0015
            lng_jitter = math.cos(ratio * math.pi) * 0.0012
            polyline.append({
                "lat": round(origin_lat + (dest_lat - origin_lat) * ratio + lat_jitter, 6),
                "lng": round(origin_lng + (dest_lng - origin_lng) * ratio + lng_jitter, 6)
            })

        steps = [
            {"instruction": "Head northeast on Main Arterial Rd toward Downtown", "distance": "800 m", "duration": "3 min"},
            {"instruction": "Turn right onto Commercial Boulevard at the roundabout", "distance": "1.1 km", "duration": "4 min"},
            {"instruction": "Keep left at the junction following signage for Parking Entry", "distance": "350 m", "duration": "1 min"},
            {"instruction": f"Arrive at {destination_name} (Automated Barrier Gate 1)", "distance": "150 m", "duration": "1 min"}
        ]

        return {
            "origin": {"lat": origin_lat, "lng": origin_lng},
            "destination_coords": {"lat": dest_lat, "lng": dest_lng},
            "destination_name": destination_name,
            "distance": f"{dist_km} km",
            "distance_km": dist_km,
            "estimated_time": f"{duration_mins} min",
            "duration_minutes": duration_mins,
            "route_provider": "Demo Route Simulation (Google Directions API compatible)",
            "polyline": polyline,
            "steps": steps
        }
