from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.detection_service import get_detection_service
from app.services.recommendation_service import RecommendationService
from app.core.config import settings
from app.schemas.analytics import (
    AIStatusResponse, AIPredictionsResponse, AIInsightsResponse
)
from app.schemas.navigation import RecommendationsResponse

router = APIRouter(tags=["AI & Insights"])

@router.get("/ai/status", response_model=AIStatusResponse, summary="AI CV Engine Detection Status")
def get_ai_status():
    """
    Returns AI vision system status, model type, detection confidence, and active mode.
    Clearly discloses DEMO MODE when real hardware/weights are not connected.
    """
    det_service = get_detection_service(mode=settings.AI_MODE)
    res = det_service.get_detection_results()
    return AIStatusResponse(
        mode=res["mode"],
        status=res["status"],
        model=res["model"],
        detection_confidence=res["detection_confidence"],
        last_analyzed=res["last_analyzed"],
        camera_count=res["camera_count"],
        label=res.get("label", "DEMO MODE — Simulated real-time detection")
    )

@router.get("/ai/predictions", response_model=AIPredictionsResponse, summary="Predictive hourly occupancy forecast")
def get_ai_predictions(db: Session = Depends(get_db)):
    """
    Returns predicted parking occupancy for upcoming hours.
    Explicitly labeled as DEMO AI PREDICTION.
    """
    return AnalyticsService.get_ai_predictions(db)

@router.get("/ai/insights", response_model=AIInsightsResponse, summary="Dynamic AI operational insights")
def get_ai_insights(db: Session = Depends(get_db)):
    """
    Generates dynamic, data-driven operational insights based on current parking bay and incident data.
    """
    insights = AnalyticsService.generate_ai_insights(db)
    from datetime import datetime
    return AIInsightsResponse(
        generated_at=datetime.utcnow().isoformat() + "Z",
        insights=insights
    )

@router.get("/recommendations", response_model=RecommendationsResponse, summary="Smart parking recommendations")
def get_recommendations(
    latitude: float = Query(12.9716, description="Driver latitude", ge=-90.0, le=90.0),
    longitude: float = Query(77.5946, description="Driver longitude", ge=-180.0, le=180.0),
    destination: Optional[str] = Query("Commercial Center", description="Target destination name"),
    sort_by: str = Query("balanced", description="Sort criteria: distance, availability, price, ev, balanced"),
    db: Session = Depends(get_db)
):
    """
    Returns transparently scored parking facility recommendations based on:
    Availability (35%), Proximity (30%), Price (20%), and EV Capability (15%).
    """
    recs = RecommendationService.get_recommendations(
        db=db,
        latitude=latitude,
        longitude=longitude,
        destination=destination,
        sort_by=sort_by
    )
    return RecommendationsResponse(
        destination=destination,
        sort_by=sort_by,
        total_found=len(recs),
        recommendations=recs
    )
