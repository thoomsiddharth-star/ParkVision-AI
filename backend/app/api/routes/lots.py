from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.services.parking_service import ParkingService
from app.schemas.lot import ParkingLotResponse, ParkingLotDetailResponse

router = APIRouter(tags=["Lots"])

@router.get("/lots", response_model=List[ParkingLotResponse], summary="List all parking lots")
def list_lots(db: Session = Depends(get_db)):
    """
    Retrieve all managed parking facilities.
    """
    return ParkingService.get_lots(db)

@router.get("/lots/{lot_id}", response_model=ParkingLotDetailResponse, summary="Get parking lot details")
def get_lot(lot_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details for a specific parking lot facility.
    """
    return ParkingService.get_lot_by_id(db, lot_id)
