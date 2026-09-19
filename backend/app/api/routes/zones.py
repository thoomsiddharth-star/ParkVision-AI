from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.models.zone import Zone
from app.models.parking_space import ParkingSpace
from app.models.system_log import SystemLog
from app.schemas.parking_platform import (
    ZoneCreate, ZoneUpdate, ZoneResponse
)

router = APIRouter(prefix="/zones", tags=["Zones"])

def compute_zone_stats(zone: Zone, db: Session) -> dict:
    count = db.query(ParkingSpace).filter(ParkingSpace.zone_id == zone.id).count()
    return {
        "id": zone.id,
        "floor_id": zone.floor_id,
        "name": zone.name,
        "description": zone.description,
        "created_at": zone.created_at,
        "total_spaces": count
    }

@router.get("", response_model=List[ZoneResponse])
def get_zones(
    floor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Zone)
    if floor_id is not None:
        query = query.filter(Zone.floor_id == floor_id)
    zones = query.order_by(Zone.name.asc()).all()
    return [compute_zone_stats(z, db) for z in zones]

@router.get("/{id}", response_model=ZoneResponse)
def get_zone(id: int, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return compute_zone_stats(zone, db)

@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
    data: ZoneCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    zone = Zone(
        floor_id=data.floor_id,
        name=data.name,
        description=data.description
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="CREATE_ZONE",
        entity_type="Zone",
        entity_id=str(zone.id),
        description=f"Created zone '{zone.name}'"
    )
    db.add(log)
    db.commit()

    return compute_zone_stats(zone, db)

@router.put("/{id}", response_model=ZoneResponse)
def update_zone(
    id: int,
    data: ZoneUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    zone = db.query(Zone).filter(Zone.id == id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(zone, key, val)

    db.commit()
    db.refresh(zone)

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="UPDATE_ZONE",
        entity_type="Zone",
        entity_id=str(zone.id),
        description=f"Updated zone '{zone.name}'"
    )
    db.add(log)
    db.commit()

    return compute_zone_stats(zone, db)

@router.delete("/{id}")
def delete_zone(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    zone = db.query(Zone).filter(Zone.id == id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    name = zone.name
    # Unassign spaces from this zone
    db.query(ParkingSpace).filter(ParkingSpace.zone_id == zone.id).update({"zone_id": None})
    db.delete(zone)
    db.commit()

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="DELETE_ZONE",
        entity_type="Zone",
        entity_id=str(id),
        description=f"Deleted zone '{name}'"
    )
    db.add(log)
    db.commit()

    return {"success": True, "message": f"Zone '{name}' deleted successfully"}
