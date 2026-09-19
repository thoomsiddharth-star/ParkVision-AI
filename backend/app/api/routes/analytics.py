from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    OccupancyAnalyticsResponse, DemandAnalyticsResponse,
    PeakHoursAnalyticsResponse, ParkingDurationAnalyticsResponse,
    EVUtilizationAnalyticsResponse
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/occupancy", response_model=OccupancyAnalyticsResponse, summary="Get historical occupancy trends")
def get_occupancy(
    period: str = Query("today", description="Analytics period: today, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """
    Returns time-series occupancy percentages formatted directly for Recharts / Chart.js.
    """
    return AnalyticsService.get_occupancy_analytics(db, period=period)

@router.get("/demand", response_model=DemandAnalyticsResponse, summary="Get traffic flow and demand level metrics")
def get_demand(
    period: str = Query("today", description="Analytics period: today, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """
    Returns vehicle turnover and demand level distributions.
    """
    return AnalyticsService.get_demand_analytics(db, period=period)

@router.get("/peak-hours", response_model=PeakHoursAnalyticsResponse, summary="Get peak hours analysis")
def get_peak_hours(
    period: str = Query("today", description="Analytics period: today, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """
    Returns peak rush intervals and occupancy probabilities.
    """
    return AnalyticsService.get_peak_hours(db, period=period)

@router.get("/parking-duration", response_model=ParkingDurationAnalyticsResponse, summary="Get parking duration distribution")
def get_parking_duration(
    period: str = Query("today", description="Analytics period: today, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """
    Returns duration brackets showing how long vehicles stay parked.
    """
    return AnalyticsService.get_parking_duration(db, period=period)

@router.get("/ev-utilization", response_model=EVUtilizationAnalyticsResponse, summary="Get EV charger utilization stats")
def get_ev_utilization(
    period: str = Query("today", description="Analytics period: today, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """
    Returns EV charging station usage across lots.
    """
    return AnalyticsService.get_ev_utilization(db, period=period)
