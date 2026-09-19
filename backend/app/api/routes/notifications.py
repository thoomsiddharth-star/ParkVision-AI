from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.parking_platform import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Notification)
    if current_user.role != "ADMIN":
        query = query.filter((Notification.user_id == current_user.id) | (Notification.user_id == None))
    return query.order_by(Notification.created_at.desc()).limit(20).all()

@router.patch("/{id}/read")
def mark_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = db.query(Notification).filter(Notification.id == id).first()
    if notif:
        notif.read = True
        db.commit()
    return {"success": True}
