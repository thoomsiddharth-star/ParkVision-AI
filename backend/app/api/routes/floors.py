import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.database.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.models.floor import Floor
from app.models.parking_space import ParkingSpace
from app.models.zone import Zone
from app.models.system_log import SystemLog
from app.schemas.parking_platform import (
    FloorCreate, FloorUpdate, FloorResponse
)

router = APIRouter(prefix="/floors", tags=["Floors"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "uploads"))
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB

def compute_floor_stats(floor: Floor, db: Session) -> dict:
    spaces = db.query(ParkingSpace).filter(ParkingSpace.floor_id == floor.id).all()
    total = len(spaces)
    available = 0
    occupied = 0
    reserved = 0
    blocked = 0
    
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
        "id": floor.id,
        "parking_location_id": floor.parking_location_id,
        "name": floor.name,
        "floor_number": floor.floor_number,
        "floor_plan_url": floor.floor_plan_url,
        "floor_plan_width": floor.floor_plan_width or 1200,
        "floor_plan_height": floor.floor_plan_height or 800,
        "created_at": floor.created_at,
        "updated_at": floor.updated_at,
        "total_spaces": total,
        "available_spaces": available,
        "occupied_spaces": occupied,
        "reserved_spaces": reserved,
        "blocked_spaces": blocked,
        "occupancy_rate": occ_rate
    }

@router.get("", response_model=List[FloorResponse])
def get_floors(
    parking_location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Floor)
    if parking_location_id is not None:
        query = query.filter(Floor.parking_location_id == parking_location_id)
    floors = query.order_by(Floor.floor_number.asc()).all()
    return [compute_floor_stats(f, db) for f in floors]

@router.get("/{id}", response_model=FloorResponse)
def get_floor(id: int, db: Session = Depends(get_db)):
    floor = db.query(Floor).filter(Floor.id == id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return compute_floor_stats(floor, db)

@router.post("", response_model=FloorResponse, status_code=status.HTTP_201_CREATED)
def create_floor(
    data: FloorCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    floor = Floor(
        parking_location_id=data.parking_location_id,
        name=data.name,
        floor_number=data.floor_number,
        floor_plan_url=data.floor_plan_url,
        floor_plan_width=data.floor_plan_width or 1200,
        floor_plan_height=data.floor_plan_height or 800
    )
    db.add(floor)
    db.commit()
    db.refresh(floor)

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="CREATE_FLOOR",
        entity_type="Floor",
        entity_id=str(floor.id),
        description=f"Created floor '{floor.name}' (Level {floor.floor_number})"
    )
    db.add(log)
    db.commit()

    return compute_floor_stats(floor, db)

@router.put("/{id}", response_model=FloorResponse)
def update_floor(
    id: int,
    data: FloorUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    floor = db.query(Floor).filter(Floor.id == id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(floor, key, val)
        
    db.commit()
    db.refresh(floor)

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="UPDATE_FLOOR",
        entity_type="Floor",
        entity_id=str(floor.id),
        description=f"Updated floor '{floor.name}'"
    )
    db.add(log)
    db.commit()

    return compute_floor_stats(floor, db)

@router.delete("/{id}")
def delete_floor(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    floor = db.query(Floor).filter(Floor.id == id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    name = floor.name
    db.delete(floor)
    db.commit()

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="DELETE_FLOOR",
        entity_type="Floor",
        entity_id=str(id),
        description=f"Deleted floor '{name}'"
    )
    db.add(log)
    db.commit()

    return {"success": True, "message": f"Floor '{name}' deleted successfully"}

@router.post("/{id}/floor-plan", response_model=FloorResponse)
async def upload_floor_plan(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    floor = db.query(Floor).filter(Floor.id == id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: PNG, JPG, JPEG, WEBP, SVG."
        )

    # Read content and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 15MB.")

    # Save to uploads directory
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"floor_{id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    # Try detecting dimensions
    width, height = 1200, 800
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(content))
        width, height = img.size
    except Exception:
        pass

    action_name = "REPLACE_FLOOR_PLAN" if floor.floor_plan_url else "UPLOAD_FLOOR_PLAN"
    floor.floor_plan_url = f"/uploads/{filename}"
    floor.floor_plan_width = width
    floor.floor_plan_height = height
    db.commit()
    db.refresh(floor)

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action=action_name,
        entity_type="Floor",
        entity_id=str(floor.id),
        description=f"{'Replaced' if action_name == 'REPLACE_FLOOR_PLAN' else 'Uploaded'} floor plan for floor '{floor.name}' ({width}x{height})"
    )
    db.add(log)
    db.commit()

    return compute_floor_stats(floor, db)

@router.delete("/{id}/floor-plan")
def remove_floor_plan(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    floor = db.query(Floor).filter(Floor.id == id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    floor.floor_plan_url = None
    db.commit()

    log = SystemLog(
        actor_id=admin.id,
        actor_name=admin.name or admin.email,
        action="DELETE_FLOOR_PLAN",
        entity_type="Floor",
        entity_id=str(floor.id),
        description=f"Removed floor plan for floor '{floor.name}'"
    )
    db.add(log)
    db.commit()

    return {"success": True, "message": "Floor plan removed successfully"}
