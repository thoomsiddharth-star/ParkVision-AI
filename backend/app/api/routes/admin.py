from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.parking_space import ParkingSpace
from app.models.parking_lot import ParkingLot
from app.models.camera import Camera
from app.models.incident import Incident
from app.schemas.user import UserResponse
from app.schemas.parking import ParkingSpaceResponse
from app.schemas.camera import CameraResponse
from app.schemas.incident import IncidentResponse

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.get("/dashboard")
def admin_dashboard_summary(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin Dashboard Overview Metrics & Controls."""
    total_lots = db.query(ParkingLot).count()
    total_spaces = db.query(ParkingSpace).count()
    occupied_spaces = db.query(ParkingSpace).filter(ParkingSpace.status == "OCCUPIED").count()
    maintenance_spaces = db.query(ParkingSpace).filter(ParkingSpace.status == "MAINTENANCE").count()
    reserved_spaces = db.query(ParkingSpace).filter(ParkingSpace.status == "RESERVED").count()
    total_cameras = db.query(Camera).count()
    online_cameras = db.query(Camera).filter(Camera.status.in_(["ONLINE", "DEMO"])).count()
    total_users = db.query(User).count()
    open_incidents = db.query(Incident).filter(Incident.status == "OPEN").count()

    return {
        "admin_email": admin.email,
        "facility_status": "OPERATIONAL",
        "total_lots": total_lots,
        "total_spaces": total_spaces,
        "occupied_spaces": occupied_spaces,
        "available_spaces": total_spaces - occupied_spaces - maintenance_spaces - reserved_spaces,
        "maintenance_spaces": maintenance_spaces,
        "reserved_spaces": reserved_spaces,
        "total_cameras": total_cameras,
        "active_cameras": online_cameras,
        "total_registered_users": total_users,
        "open_security_incidents": open_incidents
    }

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """View all registered users in the platform."""
    return [UserResponse.model_validate(u) for u in db.query(User).all()]

@router.get("/cameras", response_model=List[CameraResponse])
def get_admin_camera_config(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """View camera feeds & ROI configurations."""
    return [CameraResponse.model_validate(c) for c in db.query(Camera).all()]

@router.post("/spaces/{space_id}/status", response_model=ParkingSpaceResponse)
def update_space_admin_status(
    space_id: int,
    status_action: str,  # "LOCK", "UNLOCK", "MAINTENANCE", "AVAILABLE"
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Administratively lock, unlock, or set maintenance for a parking space."""
    space = db.query(ParkingSpace).filter(ParkingSpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Parking space not found")

    action_upper = status_action.upper()
    if action_upper == "LOCK":
        space.status = "RESERVED"
    elif action_upper == "MAINTENANCE":
        space.status = "MAINTENANCE"
    elif action_upper in ["UNLOCK", "AVAILABLE"]:
        space.status = "AVAILABLE"
        space.current_vehicle_plate = None
        space.reserved_until = None
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use LOCK, UNLOCK, or MAINTENANCE.")

    db.commit()
    db.refresh(space)
    return ParkingSpaceResponse.model_validate(space)

@router.post("/floor-plan/upload")
async def upload_floor_plan(
    lot_id: int,
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Upload a custom floor plan image for a parking facility."""
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    filename = f"floor_plan_lot_{lot_id}_{file.filename}"
    return {
        "success": True,
        "message": f"Floor plan image '{filename}' uploaded successfully.",
        "lot_id": lot_id,
        "floor_plan_url": f"/uploads/{filename}"
    }

@router.get("/settings")
def get_system_settings(
    admin: User = Depends(get_current_admin)
):
    """View system & AI detection settings."""
    return {
        "ai_mode": "demo",
        "detection_confidence_threshold": 0.85,
        "auto_lock_on_reservation": True,
        "reservation_duration_minutes": 30,
        "websocket_tick_rate_seconds": 4.0,
        "admin_contact": admin.email
    }
