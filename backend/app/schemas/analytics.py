from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OccupancyDataPoint(BaseModel):
    time: str
    occupancy: float
    available: Optional[int] = None
    occupied: Optional[int] = None

class OccupancyAnalyticsResponse(BaseModel):
    period: str
    data: List[OccupancyDataPoint]

class DemandDataPoint(BaseModel):
    time: str
    demand_level: str  # Low, Moderate, High, Peak
    turnover_rate: float
    vehicles_entered: int
    vehicles_exited: int

class DemandAnalyticsResponse(BaseModel):
    period: str
    data: List[DemandDataPoint]

class PeakHourDataPoint(BaseModel):
    hour: str
    average_occupancy: float
    peak_probability: float

class PeakHoursAnalyticsResponse(BaseModel):
    period: str
    busiest_time: str
    data: List[PeakHourDataPoint]

class DurationDataPoint(BaseModel):
    duration_bracket: str  # e.g., "< 1 hr", "1-2 hrs", "2-4 hrs", "> 4 hrs"
    percentage: float
    vehicle_count: int

class ParkingDurationAnalyticsResponse(BaseModel):
    period: str
    average_duration: str
    data: List[DurationDataPoint]

class EVUtilizationDataPoint(BaseModel):
    lot_name: str
    total_ev_spots: int
    occupied_ev_spots: int
    utilization_rate: float

class EVUtilizationAnalyticsResponse(BaseModel):
    period: str
    overall_ev_utilization: float
    data: List[EVUtilizationDataPoint]

class AIStatusResponse(BaseModel):
    mode: str = "demo"
    status: str = "active"
    model: str = "YOLO"
    detection_confidence: float = 97.4
    last_analyzed: str
    camera_count: int
    label: str = "DEMO MODE — Simulated real-time detection"

class AIPredictionItem(BaseModel):
    time: str
    occupancy_percentage: float
    confidence: float

class AIPredictionsResponse(BaseModel):
    label: str = "DEMO AI PREDICTION"
    disclaimer: str = "Deterministic demo prediction algorithm for prototype demonstration. Not a trained model."
    generated_at: str
    predictions: List[AIPredictionItem]

class AIInsightsResponse(BaseModel):
    generated_at: str
    insights: List[str]
