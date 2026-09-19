from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.database.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.models.parking_location import ParkingLocation
from app.models.floor import Floor
from app.models.parking_space import ParkingSpace
from app.models.system_log import SystemLog
from app.schemas.parking_platform import (
    LocationCreate, LocationUpdate, LocationResponse
)

router = APIRouter(prefix="/parking-locations", tags=["Parking Locations"])

def compute_location_stats(loc: ParkingLocation, db: Session) -> dict:
    floors = db.query(Floor).filter(Floor.parking_location_id == loc.id).all()
    floor_ids = [f.id for f in floors]
    
    total = 0
    available = 0
    occupied = 0
    reserved = 0
    blocked = 0
    
    if floor_ids:
        spaces = db.query(ParkingSpace).filter(ParkingSpace.floor_id.in_(floor_ids)).all()
        total = len(spaces)
        for s in spaces:
            st = (s.status or "").upper()
            if st == "AVAILABLE":
                available += 1
            elif st == "OCCUPIED":
                occupied += 1
            elif st == "RESERVED":
                reserved += 1
            elif st == "BLOCKED":
                blocked += 1
                
    occ_rate = round((occupied / total * 100), 1) if total > 0 else 0.0
    
    return {
        "id": loc.id,
        "name": loc.name,
        "address": loc.address,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "description": loc.description,
        "operating_hours": loc.operating_hours,
        "pricing": loc.pricing,
        "status": loc.status,
        "created_at": loc.created_at,
        "floor_count": len(floors),
        "total_spaces": total,
        "available_spaces": available,
        "occupied_spaces": occupied,
        "reserved_spaces": reserved,
        "blocked_spaces": blocked,
        "occupancy_rate": occ_rate
    }

@router.get("", response_model=List[LocationResponse])
def get_locations(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ParkingLocation)
    if search:
        query = query.filter(ParkingLocation.name.ilike(f"%{search}%") | ParkingLocation.address.ilike(f"%{search}%"))
    locations = query.order_by(ParkingLocation.id.asc()).all()
    return [compute_location_stats(loc, db) for loc in locations]

@router.get("/{id}", response_model=LocationResponse)
def get_location(id: int, db: Session = Depends(get_db)):
    loc = db.query(ParkingLocation).filter(ParkingLocation.id == id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Parking location not found")
    return compute_location_stats(loc, db)

@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    data: LocationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    loc = ParkingLocation(
        name=data.name,
        address=data.address,
        latitude=data.latitude,
        longitude=data.longitude,
        description=data.description,
        operating_hours=data.operating_hours,
        pricing=data.pricing,
        status=data.status or "Open"
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)

    # Log action
    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="CREATE_LOCATION",
        entity_type="ParkingLocation",
        entity_id=str(loc.id),
        description=f"Created parking location '{loc.name}' at {loc.address}"
    )
    db.add(log)
    db.commit()

    return compute_location_stats(loc, db)

@router.put("/{id}", response_model=LocationResponse)
def update_location(
    id: int,
    data: LocationUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    loc = db.query(ParkingLocation).filter(ParkingLocation.id == id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Parking location not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(loc, key, val)
        
    db.commit()
    db.refresh(loc)

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="UPDATE_LOCATION",
        entity_type="ParkingLocation",
        entity_id=str(loc.id),
        description=f"Updated parking location '{loc.name}'"
    )
    db.add(log)
    db.commit()

    return compute_location_stats(loc, db)

@router.delete("/{id}")
def delete_location(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    loc = db.query(ParkingLocation).filter(ParkingLocation.id == id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Parking location not found")
    
    name = loc.name
    db.delete(loc)
    db.commit()

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="DELETE_LOCATION",
        entity_type="ParkingLocation",
        entity_id=str(id),
        description=f"Deleted parking location '{name}'"
    )
    db.add(log)
    db.commit()

    return {"success": True, "message": f"Parking location '{name}' deleted successfully"}
