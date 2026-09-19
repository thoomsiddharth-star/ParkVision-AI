from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.services.camera_service import CameraService
from app.schemas.camera import CameraResponse, CameraStatusResponse

router = APIRouter(tags=["Cameras"])

@router.get("/cameras", response_model=List[CameraResponse], summary="List all CCTV and detection cameras")
def list_cameras(db: Session = Depends(get_db)):
    """
    Retrieve all CCTV cameras configured across parking lots.
    """
    return CameraService.get_all_cameras(db)

@router.get("/cameras/{camera_id}", response_model=CameraResponse, summary="Get camera by ID")
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Retrieve camera configuration and metadata.
    """
    return CameraService.get_camera_by_id(db, camera_id)

@router.get("/cameras/{camera_id}/status", response_model=CameraStatusResponse, summary="Get camera stream & telemetry status")
def get_camera_status(camera_id: int, db: Session = Depends(get_db)):
    """
    Retrieve real-time camera telemetry: FPS, detection confidence, cars/spaces detected, and stream status.
    """
    return CameraService.get_camera_status(db, camera_id)
