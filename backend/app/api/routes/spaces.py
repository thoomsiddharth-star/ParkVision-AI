from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.database.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.models.parking_space import ParkingSpace
from app.models.floor import Floor
from app.models.zone import Zone
from app.models.system_log import SystemLog
from app.services.websocket_manager import ws_manager
from app.schemas.parking_platform import (
    ParkingSpaceCreate, ParkingSpaceUpdate, ParkingSpaceBatchRequest,
    ParkingSpaceResponse, ParkingSpaceStatusUpdate
)

router = APIRouter(prefix="/parking-spaces", tags=["Parking Spaces"])

def enrich_space(space: ParkingSpace) -> dict:
    return {
        "id": space.id,
        "floor_id": space.floor_id,
        "zone_id": space.zone_id,
        "space_code": space.space_code,
        "name": space.name or space.space_code,
        "type": space.type,
        "status": space.status,
        "x": space.x,
        "y": space.y,
        "width": space.width,
        "height": space.height,
        "rotation": space.rotation,
        "price": space.price,
        "notes": space.notes,
        "created_at": space.created_at,
        "updated_at": space.updated_at,
        "zone_name": space.zone.name if space.zone else None,
        "floor_name": space.floor.name if space.floor else None
    }

@router.get("", response_model=List[ParkingSpaceResponse])
def get_spaces(
    floor_id: Optional[int] = None,
    zone_id: Optional[int] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ParkingSpace)
    if floor_id is not None:
        query = query.filter(ParkingSpace.floor_id == floor_id)
    if zone_id is not None:
        query = query.filter(ParkingSpace.zone_id == zone_id)
    if status and status.upper() != "ALL":
        query = query.filter(ParkingSpace.status.ilike(status))
    if type and type.upper() != "ALL":
        query = query.filter(ParkingSpace.type.ilike(type))
    if search:
        query = query.filter(
            ParkingSpace.space_code.ilike(f"%{search}%") | 
            ParkingSpace.name.ilike(f"%{search}%") |
            ParkingSpace.notes.ilike(f"%{search}%")
        )
    spaces = query.order_by(ParkingSpace.space_code.asc()).all()
    return [enrich_space(s) for s in spaces]

@router.get("/{id}", response_model=ParkingSpaceResponse)
def get_space(id: int, db: Session = Depends(get_db)):
    space = db.query(ParkingSpace).filter(ParkingSpace.id == id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Parking space not found")
    return enrich_space(space)

@router.post("", response_model=ParkingSpaceResponse, status_code=status.HTTP_201_CREATED)
async def create_space(
    data: ParkingSpaceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    # Check duplicate space_code on same floor
    existing = db.query(ParkingSpace).filter(
        ParkingSpace.floor_id == data.floor_id,
        ParkingSpace.space_code.ilike(data.space_code)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Parking space code '{data.space_code}' already exists on this floor."
        )

    space = ParkingSpace(
        floor_id=data.floor_id,
        zone_id=data.zone_id,
        space_code=data.space_code,
        name=data.name or data.space_code,
        type=data.type or "Normal",
        status=data.status or "Available",
        x=data.x,
        y=data.y,
        width=data.width,
        height=data.height,
        rotation=data.rotation,
        price=data.price,
        notes=data.notes
    )
    db.add(space)
    db.commit()
    db.refresh(space)

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="CREATE_SPACE",
        entity_type="ParkingSpace",
        entity_id=str(space.id),
        description=f"Created parking space '{space.space_code}' ({space.type}, status: {space.status})"
    )
    db.add(log)
    db.commit()

    # Broadcast update
    await ws_manager.broadcast_space_update(space.id, space.space_code, space.status)

    return enrich_space(space)

@router.post("/batch", response_model=List[ParkingSpaceResponse])
async def batch_update_spaces(
    data: ParkingSpaceBatchRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Saves and updates multiple spaces layout coordinates directly from the Floor Plan Editor.
    """
    floor = db.query(Floor).filter(Floor.id == data.floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    saved_spaces = []
    seen_codes = set()

    for item in data.spaces:
        code = item.space_code.strip()
        if code.lower() in seen_codes:
            continue
        seen_codes.add(code.lower())

        space = None
        if item.id:
            space = db.query(ParkingSpace).filter(ParkingSpace.id == item.id).first()

        if not space:
            # Check by code on this floor
            space = db.query(ParkingSpace).filter(
                ParkingSpace.floor_id == data.floor_id,
                ParkingSpace.space_code.ilike(code)
            ).first()

        if space:
            space.space_code = code
            if item.name:
                space.name = item.name
            space.type = item.type
            if item.status:
                space.status = item.status
            space.zone_id = item.zone_id
            space.x = max(0.0, min(1.0, item.x))
            space.y = max(0.0, min(1.0, item.y))
            space.width = max(0.01, min(1.0, item.width))
            space.height = max(0.01, min(1.0, item.height))
            space.rotation = item.rotation
            space.price = item.price
            if item.notes is not None:
                space.notes = item.notes
        else:
            space = ParkingSpace(
                floor_id=data.floor_id,
                zone_id=item.zone_id,
                space_code=code,
                name=item.name or code,
                type=item.type or "Normal",
                status=item.status or "Available",
                x=max(0.0, min(1.0, item.x)),
                y=max(0.0, min(1.0, item.y)),
                width=max(0.01, min(1.0, item.width)),
                height=max(0.01, min(1.0, item.height)),
                rotation=item.rotation,
                price=item.price,
                notes=item.notes
            )
            db.add(space)

        db.flush()
        saved_spaces.append(space)

    db.commit()

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="BATCH_LAYOUT_SAVED",
        entity_type="Floor",
        entity_id=str(floor.id),
        description=f"Saved layout for floor '{floor.name}' with {len(saved_spaces)} spaces"
    )
    db.add(log)
    db.commit()

    return [enrich_space(s) for s in saved_spaces]

@router.put("/{id}", response_model=ParkingSpaceResponse)
async def update_space(
    id: int,
    data: ParkingSpaceUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    space = db.query(ParkingSpace).filter(ParkingSpace.id == id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Parking space not found")

    old_status = space.status
    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(space, key, val)

    db.commit()
    db.refresh(space)

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="UPDATE_SPACE",
        entity_type="ParkingSpace",
        entity_id=str(space.id),
        description=f"Updated space '{space.space_code}' (Status: {space.status}, Type: {space.type})"
    )
    db.add(log)
    db.commit()

    if old_status != space.status:
        await ws_manager.broadcast_space_update(space.id, space.space_code, space.status)

    return enrich_space(space)

@router.patch("/{id}/status", response_model=ParkingSpaceResponse)
async def update_space_status(
    id: int,
    data: ParkingSpaceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space = db.query(ParkingSpace).filter(ParkingSpace.id == id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Parking space not found")

    valid_statuses = {"Available", "Occupied", "Reserved", "Blocked"}
    normalized = data.status.capitalize()
    if normalized not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{data.status}'. Must be one of: {valid_statuses}")

    old_status = space.status
    space.status = normalized
    db.commit()
    db.refresh(space)

    log = SystemLog(
        actor_id=current_user.id,
        actor_name=current_user.name or current_user.email,
        action="STATUS_CHANGE",
        entity_type="ParkingSpace",
        entity_id=str(space.id),
        description=f"Status changed from '{old_status}' to '{normalized}' for space '{space.space_code}'"
    )
    db.add(log)
    db.commit()

    await ws_manager.broadcast_space_update(space.id, space.space_code, space.status)

    return enrich_space(space)

@router.delete("/{id}")
def delete_space(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    space = db.query(ParkingSpace).filter(ParkingSpace.id == id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Parking space not found")

    code = space.space_code
    db.delete(space)
    db.commit()

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="DELETE_SPACE",
        entity_type="ParkingSpace",
        entity_id=str(id),
        description=f"Deleted parking space '{code}'"
    )
    db.add(log)
    db.commit()

    return {"success": True, "message": f"Parking space '{code}' deleted successfully"}
