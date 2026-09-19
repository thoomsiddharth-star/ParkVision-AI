import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.parking_lot import ParkingLot
from app.models.parking_space import ParkingSpace

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class RecommendationService:
    @staticmethod
    def get_recommendations(
        db: Session,
        latitude: float,
        longitude: float,
        destination: Optional[str] = None,
        sort_by: str = "balanced"
    ) -> List[Dict[str, Any]]:
        lots = db.query(ParkingLot).all()
        results = []

        for lot in lots:
            dist_km = haversine_distance_km(latitude, longitude, lot.latitude, lot.longitude)
            
            # Count EV and Accessible spaces available
            spaces = db.query(ParkingSpace).filter(ParkingSpace.parking_lot_id == lot.id).all()
            ev_available = sum(1 for s in spaces if s.space_type == "EV" and s.status == "AVAILABLE")
            accessible_available = sum(1 for s in spaces if s.space_type == "ACCESSIBLE" and s.status == "AVAILABLE")

            # Scoring Components (0 to 100 each)
            # 1. Availability Score (0-100)
            avail_ratio = (lot.available_spaces / lot.capacity) if lot.capacity > 0 else 0.0
            avail_score = avail_ratio * 100.0

            # 2. Distance/Proximity Score (0-100) - closer is higher
            prox_score = max(0.0, 100.0 - (dist_km / 10.0) * 100.0)

            # 3. Price Score (0-100) - cheaper is higher (benchmark ₹100/hr)
            price_score = max(0.0, 100.0 - (lot.price_per_hour / 100.0) * 100.0)

            # 4. EV Capability Score (0-100)
            ev_score = min(100.0, ev_available * 25.0)

            # Balanced Composite Weighted Score
            composite_score = round(
                (0.35 * avail_score) +
                (0.30 * prox_score) +
                (0.20 * price_score) +
                (0.15 * ev_score),
                1
            )

            # Formatting distance string
            dist_str = f"{dist_km} km" if dist_km >= 1.0 else f"{int(dist_km * 1000)} m"

            results.append({
                "parking_lot_id": lot.id,
                "name": lot.name,
                "address": lot.address,
                "distance": dist_str,
                "distance_km": dist_km,
                "available_spaces": lot.available_spaces,
                "occupancy_percentage": lot.occupancy_percentage,
                "price_per_hour": lot.price_per_hour,
                "walking_time": lot.walking_time,
                "ev_available": ev_available,
                "accessible_available": accessible_available,
                "score": composite_score,
                "score_breakdown": {
                    "availability_score": round(avail_score, 1),
                    "proximity_score": round(prox_score, 1),
                    "price_score": round(price_score, 1),
                    "ev_score": round(ev_score, 1)
                },
                "latitude": lot.latitude,
                "longitude": lot.longitude
            })

        # Sorting
        sort_key = sort_by.lower()
        if sort_key == "distance":
            results.sort(key=lambda x: x["distance_km"])
        elif sort_key == "availability":
            results.sort(key=lambda x: x["available_spaces"], reverse=True)
        elif sort_key == "price":
            results.sort(key=lambda x: x["price_per_hour"])
        elif sort_key == "ev":
            results.sort(key=lambda x: x["ev_available"], reverse=True)
        else:  # balanced
            results.sort(key=lambda x: x["score"], reverse=True)

        return results

    @staticmethod
    def driver_search(
        db: Session,
        latitude: float,
        longitude: float,
        destination: str,
        max_distance_km: Optional[float] = 10.0,
        max_price: Optional[float] = None,
        ev_required: bool = False,
        accessible_required: bool = False
    ) -> List[Dict[str, Any]]:
        all_recs = RecommendationService.get_recommendations(
            db=db,
            latitude=latitude,
            longitude=longitude,
            destination=destination,
            sort_by="balanced"
        )

        filtered = []
        for r in all_recs:
            if max_distance_km is not None and r["distance_km"] > max_distance_km:
                continue
            if max_price is not None and r["price_per_hour"] > max_price:
                continue
            if ev_required and r["ev_available"] <= 0:
                continue
            if accessible_required and r["accessible_available"] <= 0:
                continue
            filtered.append(r)

        return filtered
