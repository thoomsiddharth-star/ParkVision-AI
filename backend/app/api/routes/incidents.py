from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.incident import Incident
from app.models.parking_lot import ParkingLot
from app.schemas.incident import (
    IncidentResponse, IncidentActionResponse, IncidentStatusEnum
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])

def format_incident(inc: Incident, db: Session) -> IncidentResponse:
    lot_name = inc.lot.name if inc.lot else None
    return IncidentResponse(
        id=inc.id,
        parking_lot_id=inc.parking_lot_id,
        camera_id=None,
        type=inc.type,
        severity=inc.severity,
        description=inc.description,
        timestamp=inc.timestamp,
        status=inc.status,
        lot_name=lot_name,
        camera_name=None
    )

@router.get("", response_model=List[IncidentResponse], summary="List all security and parking incidents")
def list_incidents(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all detected parking violations and security incidents (e.g. double parking, blocked emergency lanes).
    """
    query = db.query(Incident)
    if status_filter:
        query = query.filter(Incident.status == status_filter.upper())
    incidents = query.order_by(Incident.timestamp.desc()).all()
    return [format_incident(inc, db) for inc in incidents]

@router.get("/{incident_id}", response_model=IncidentResponse, summary="Get incident details by ID")
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details for a specific incident.
    """
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "INCIDENT_NOT_FOUND", "message": f"Incident with ID {incident_id} not found."}
        )
    return format_incident(inc, db)

@router.post("/{incident_id}/review", response_model=IncidentActionResponse, summary="Mark incident as REVIEWED")
def review_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Transition incident status from OPEN to REVIEWED by parking lot operator.
    """
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "INCIDENT_NOT_FOUND", "message": f"Incident with ID {incident_id} not found."}
        )
    prev = inc.status
    inc.status = "REVIEWED"
    db.commit()
    db.refresh(inc)

    return IncidentActionResponse(
        success=True,
        incident_id=inc.id,
        previous_status=prev,
        new_status=inc.status,
        message=f"Incident {inc.id} marked as REVIEWED.",
        incident=format_incident(inc, db)
    )

@router.post("/{incident_id}/resolve", response_model=IncidentActionResponse, summary="Mark incident as RESOLVED")
def resolve_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Transition incident status to RESOLVED after field staff or automated clearance.
    """
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "INCIDENT_NOT_FOUND", "message": f"Incident with ID {incident_id} not found."}
        )
    prev = inc.status
    inc.status = "RESOLVED"
    db.commit()
    db.refresh(inc)

    return IncidentActionResponse(
        success=True,
        incident_id=inc.id,
        previous_status=prev,
        new_status=inc.status,
        message=f"Incident {inc.id} successfully resolved.",
        incident=format_incident(inc, db)
    )
