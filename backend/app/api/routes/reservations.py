from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime, timezone

from app.database.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.models.parking_space import ParkingSpace
from app.models.reservation import Reservation
from app.models.notification import Notification
from app.models.system_log import SystemLog
from app.services.websocket_manager import ws_manager
from app.schemas.parking_platform import (
    ReservationCreate, ReservationResponse, ReservationStatusUpdate
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])

def enrich_reservation(res: Reservation) -> dict:
    space = res.space
    floor = space.floor if space else None
    loc = floor.parking_location if floor else None
    user = res.user

    return {
        "id": res.id,
        "user_id": res.user_id,
        "parking_space_id": res.parking_space_id,
        "start_time": res.start_time,
        "end_time": res.end_time,
        "status": res.status,
        "created_at": res.created_at,
        "space_code": space.space_code if space else "N/A",
        "floor_name": floor.name if floor else "N/A",
        "location_name": loc.name if loc else "N/A",
        "user_name": user.name if user else "User",
        "user_email": user.email if user else "N/A",
        "price": space.price if space else 30.0
    }

@router.get("", response_model=List[ReservationResponse])
def get_reservations(
    status: Optional[str] = None,
    space_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Reservation)
    # If not admin, restrict to own reservations
    if current_user.role != "ADMIN":
        query = query.filter(Reservation.user_id == current_user.id)
        
    if status and status.upper() != "ALL":
        query = query.filter(Reservation.status.ilike(status))
    if space_id is not None:
        query = query.filter(Reservation.parking_space_id == space_id)
        
    reservations = query.order_by(Reservation.start_time.desc()).all()
    return [enrich_reservation(r) for r in reservations]

@router.get("/{id}", response_model=ReservationResponse)
def get_reservation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = db.query(Reservation).filter(Reservation.id == id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if current_user.role != "ADMIN" and res.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this reservation")
    return enrich_reservation(res)

@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    data: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    space = db.query(ParkingSpace).filter(ParkingSpace.id == data.parking_space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Parking space not found")

    # Cannot reserve a blocked space
    if (space.status or "").upper() == "BLOCKED":
        raise HTTPException(status_code=400, detail="This parking space is currently blocked and cannot be reserved.")

    # Validate time range
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=400, detail="Reservation end time must be after start time.")

    # DOUBLE BOOKING PREVENTION: Check overlapping active/upcoming reservations
    conflict = db.query(Reservation).filter(
        Reservation.parking_space_id == data.parking_space_id,
        Reservation.status.in_(["Upcoming", "Active"]),
        Reservation.start_time < data.end_time,
        Reservation.end_time > data.start_time
    ).first()

    if conflict:
        raise HTTPException(
            status_code=409,
            detail=f"Space '{space.space_code}' is already reserved between {conflict.start_time.strftime('%H:%M')} and {conflict.end_time.strftime('%H:%M')}. Double booking prevented."
        )

    res = Reservation(
        user_id=current_user.id,
        parking_space_id=data.parking_space_id,
        start_time=data.start_time,
        end_time=data.end_time,
        status="Active" if data.start_time <= datetime.now(timezone.utc) <= data.end_time else "Upcoming"
    )
    db.add(res)

    # Transition space status to Reserved
    old_status = space.status
    space.status = "Reserved"
    db.commit()
    db.refresh(res)

    # Create user notification
    notif = Notification(
        user_id=current_user.id,
        type="RESERVATION",
        message=f"Reservation confirmed for space '{space.space_code}' on {res.start_time.strftime('%b %d, %H:%M')}."
    )
    db.add(notif)

    # Record system log
    log = SystemLog(
        actor_id=current_user.id,
        actor_name=current_user.name or current_user.email,
        action="RESERVATION_CREATED",
        entity_type="Reservation",
        entity_id=str(res.id),
        description=f"Reserved space '{space.space_code}' from {res.start_time.strftime('%H:%M')} to {res.end_time.strftime('%H:%M')}"
    )
    db.add(log)
    db.commit()

    await ws_manager.broadcast_space_update(space.id, space.space_code, space.status)

    return enrich_reservation(res)

@router.patch("/{id}/cancel", response_model=ReservationResponse)
async def cancel_reservation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = db.query(Reservation).filter(Reservation.id == id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if current_user.role != "ADMIN" and res.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this reservation")

    res.status = "Cancelled"
    
    # Check if there are other active reservations on this space
    space = res.space
    if space:
        other_active = db.query(Reservation).filter(
            Reservation.parking_space_id == space.id,
            Reservation.id != res.id,
            Reservation.status.in_(["Upcoming", "Active"])
        ).first()
        if not other_active and space.status == "Reserved":
            space.status = "Available"
            await ws_manager.broadcast_space_update(space.id, space.space_code, space.status)

    notif = Notification(
        user_id=res.user_id,
        type="RESERVATION_CANCELLED",
        message=f"Reservation #{res.id} for space '{space.space_code if space else 'N/A'}' was cancelled."
    )
    db.add(notif)

    log = SystemLog(
        actor_id=current_user.id,
        actor_name=current_user.name or current_user.email,
        action="RESERVATION_CANCELLED",
        entity_type="Reservation",
        entity_id=str(res.id),
        description=f"Cancelled reservation #{res.id} for space '{space.space_code if space else 'N/A'}'"
    )
    db.add(log)
    db.commit()

    return enrich_reservation(res)

@router.put("/{id}/status", response_model=ReservationResponse)
async def update_reservation_status(
    id: int,
    data: ReservationStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    res = db.query(Reservation).filter(Reservation.id == id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    res.status = data.status
    db.commit()
    db.refresh(res)

    return enrich_reservation(res)
