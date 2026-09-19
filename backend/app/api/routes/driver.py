from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.recommendation_service import RecommendationService
from app.schemas.navigation import DriverSearchRequest, DriverSearchResponse

router = APIRouter(prefix="/driver", tags=["Driver Mode"])

@router.post("/search", response_model=DriverSearchResponse, summary="Find best parking based on driver preferences")
def search_driver_parking(req: DriverSearchRequest, db: Session = Depends(get_db)):
    """
    Search and filter recommended parking locations tailored to driver preferences
    such as max walking distance, max hourly rate, EV fast charging, or accessibility needs.
    """
    prefs = req.preferences
    max_dist = prefs.max_distance_km if prefs else 10.0
    max_price = prefs.max_price_per_hour if prefs else None
    ev_req = prefs.ev_required if prefs else False
    acc_req = prefs.accessible_required if prefs else False

    results = RecommendationService.driver_search(
        db=db,
        latitude=req.latitude,
        longitude=req.longitude,
        destination=req.destination or "Destination",
        max_distance_km=max_dist,
        max_price=max_price,
        ev_required=ev_req,
        accessible_required=acc_req
    )

    return DriverSearchResponse(
        destination=req.destination or "Destination",
        origin={"lat": req.latitude, "lng": req.longitude},
        matches_count=len(results),
        recommended_lots=results
    )
