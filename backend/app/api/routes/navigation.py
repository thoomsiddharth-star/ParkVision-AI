from fastapi import APIRouter, Query
from app.services.navigation_service import NavigationService
from app.schemas.navigation import NavigationResponse

router = APIRouter(tags=["Navigation"])

@router.get("/navigation", response_model=NavigationResponse, summary="Get turn-by-turn routing to parking destination")
async def get_navigation(
    origin_latitude: float = Query(..., description="Driver start latitude", ge=-90.0, le=90.0),
    origin_longitude: float = Query(..., description="Driver start longitude", ge=-180.0, le=180.0),
    destination_latitude: float = Query(..., description="Parking destination latitude", ge=-90.0, le=90.0),
    destination_longitude: float = Query(..., description="Parking destination longitude", ge=-180.0, le=180.0),
    destination_name: str = Query("Central Mall Parking", description="Name of destination")
):
    """
    Computes driving directions and route waypoints from driver location to destination.
    Uses Google Directions API if configured, otherwise supplies simulated turn-by-turn route.
    """
    return await NavigationService.get_route(
        origin_lat=origin_latitude,
        origin_lng=origin_longitude,
        dest_lat=destination_latitude,
        dest_lng=destination_longitude,
        destination_name=destination_name
    )
