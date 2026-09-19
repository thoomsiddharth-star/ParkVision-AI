from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database.database import get_db
from app.services.parking_service import ParkingService
from app.services.websocket_manager import ws_manager
from app.schemas.lot import ParkingLotResponse, ParkingLotDetailResponse
from app.schemas.parking import (
    ParkingSpaceResponse, SpaceSelectRequest, SpaceSelectResponse,
    LiveParkingResponse
)

router = APIRouter(tags=["Parking"])

@router.get("/parking/lots", response_model=List[ParkingLotResponse], summary="Get all parking lots")
def get_parking_lots(db: Session = Depends(get_db)):
    """
    Retrieve all managed parking lots with capacity, occupancy, and pricing.
    """
    return ParkingService.get_lots(db)

@router.get("/parking/lots/{lot_id}", response_model=ParkingLotDetailResponse, summary="Get parking lot by ID")
def get_parking_lot(lot_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information for a specific parking facility.
    """
    return ParkingService.get_lot_by_id(db, lot_id)

@router.get("/parking/lots/{lot_id}/spaces", response_model=List[ParkingSpaceResponse], summary="Get all spaces for a parking lot")
def get_lot_spaces(lot_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all parking spaces belonging to a specific parking lot.
    """
    return ParkingService.get_spaces_by_lot(db, lot_id)

@router.get("/parking/spaces/{space_id}", response_model=ParkingSpaceResponse, summary="Get space by ID")
def get_space(space_id: int, db: Session = Depends(get_db)):
    """
    Retrieve individual parking space details.
    """
    return ParkingService.get_space_by_id(db, space_id)

@router.post("/parking/spaces/{space_id}/select", response_model=SpaceSelectResponse, summary="Select an available parking space")
def select_space(
    space_id: int,
    req: Optional[SpaceSelectRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Select an available parking bay. Returns an error if the space is OCCUPIED or RESERVED.
    Does not permanently reserve unless permanent_reservation=True is passed.
    """
    perm = req.permanent_reservation if req else False
    return ParkingService.select_space(db, space_id, permanent_reservation=perm)

@router.get("/parking/live", response_model=LiveParkingResponse, summary="Get real-time live parking overview")
def get_live_parking(
    lot_id: Optional[int] = Query(None, description="Optional parking lot ID to filter"),
    db: Session = Depends(get_db)
):
    """
    Returns live parking statistics: total, available, occupied, reserved spaces,
    occupancy rate, and space statuses. Acts as polling fallback if WebSockets are unavailable.
    """
    return ParkingService.get_live_parking(db, lot_id)

# =====================================================================
# Backward-compatibility endpoints for prototype / legacy integrations
# =====================================================================
@router.get("/spaces", summary="Legacy spaces endpoint")
def legacy_spaces(db: Session = Depends(get_db)):
    live = ParkingService.get_live_parking(db, lot_id=1)
    return {"spaces": live["spaces"]}

@router.get("/locations", summary="Legacy locations endpoint")
def legacy_locations(db: Session = Depends(get_db)):
    lots = ParkingService.get_lots(db)
    return {"locations": lots}

@router.get("/status", summary="Legacy status endpoint")
def legacy_status(db: Session = Depends(get_db)):
    live = ParkingService.get_live_parking(db, lot_id=1)
    return {
        "total": live["total_spaces"],
        "available": live["available_spaces"],
        "occupied": live["occupied_spaces"],
        "occupancyRate": round(live["occupancy_percentage"]),
        "demoMode": True,
        "model": "YOLO Computer Vision",
        "cameraStatus": "Detection Active"
    }
