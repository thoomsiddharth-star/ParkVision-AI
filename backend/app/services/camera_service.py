from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.camera import Camera

class CameraService:
    @staticmethod
    def get_all_cameras(db: Session) -> List[Camera]:
        return db.query(Camera).order_by(Camera.id).all()

    @staticmethod
    def get_camera_by_id(db: Session, camera_id: int) -> Camera:
        cam = db.query(Camera).filter(Camera.id == camera_id).first()
        if not cam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "CAMERA_NOT_FOUND", "message": f"Camera with ID {camera_id} not found."}
            )
        return cam

    @staticmethod
    def get_camera_status(db: Session, camera_id: int) -> Dict[str, Any]:
        cam = CameraService.get_camera_by_id(db, camera_id)
        return {
            "id": cam.id,
            "name": cam.name,
            "camera_number": cam.camera_number,
            "status": cam.status,
            "cars_detected": cam.cars_detected,
            "spaces_detected": cam.spaces_detected,
            "ai_confidence": cam.ai_confidence,
            "last_analyzed_at": cam.last_analyzed_at,
            "stream_url": cam.stream_url,
            "fps": 30,
            "latency_ms": 14,
            "resolution": "1080p (1920x1080)",
            "mode": "DEMO MODE — Simulated detection feed" if not cam.stream_url else "LIVE RTSP FEED"
        }
