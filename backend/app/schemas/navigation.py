from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RecommendationItem(BaseModel):
    parking_lot_id: int
    name: str
    address: str
    distance: str
    distance_km: float
    available_spaces: int
    occupancy_percentage: float
    price_per_hour: float
    walking_time: str
    ev_available: int
    accessible_available: int
    score: float = Field(..., description="Transparent calculated score out of 100")
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    latitude: float
    longitude: float

class RecommendationsResponse(BaseModel):
    destination: Optional[str] = None
    sort_by: str
    total_found: int
    scoring_methodology: str = (
        "Transparent multi-criteria weighting: 35% Availability + 30% Proximity + 20% Price + 15% EV Capability"
    )
    recommendations: List[RecommendationItem]

class DriverPreferences(BaseModel):
    max_distance_km: Optional[float] = Field(default=10.0, ge=0.1)
    max_price_per_hour: Optional[float] = Field(default=None, ge=0.0)
    ev_required: bool = False
    accessible_required: bool = False

class DriverSearchRequest(BaseModel):
    destination: Optional[str] = "Downtown City Center"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    preferences: Optional[DriverPreferences] = Field(default_factory=DriverPreferences)

class DriverSearchResponse(BaseModel):
    destination: str
    origin: Dict[str, float]
    matches_count: int
    recommended_lots: List[RecommendationItem]

class RouteStep(BaseModel):
    instruction: str
    distance: str
    duration: str

class RouteCoordinate(BaseModel):
    lat: float
    lng: float

class NavigationResponse(BaseModel):
    origin: Dict[str, float]
    destination_coords: Dict[str, float]
    destination_name: str
    distance: str
    distance_km: float
    estimated_time: str
    duration_minutes: int
    route_provider: str = "Demo Route Simulation (Google Directions API compatible)"
    polyline: List[RouteCoordinate]
    steps: List[RouteStep]
