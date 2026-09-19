from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class IncidentTypeEnum(str, Enum):
    WRONG_WAY = "WRONG_WAY"
    DOUBLE_PARKING = "DOUBLE_PARKING"
    OUTSIDE_SPACE = "OUTSIDE_SPACE"
    BLOCKED_EMERGENCY_LANE = "BLOCKED_EMERGENCY_LANE"
    LONG_TERM_PARKING = "LONG_TERM_PARKING"
    UNAUTHORIZED_PARKING = "UNAUTHORIZED_PARKING"

class IncidentSeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class IncidentStatusEnum(str, Enum):
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    RESOLVED = "RESOLVED"

class IncidentBase(BaseModel):
    parking_lot_id: int = Field(..., gt=0)
    camera_id: Optional[int] = None
    type: IncidentTypeEnum
    severity: IncidentSeverityEnum = IncidentSeverityEnum.LOW
    description: str = Field(..., min_length=1, max_length=255)

class IncidentCreate(IncidentBase):
    pass

class IncidentResponse(IncidentBase):
    id: int
    timestamp: datetime
    status: IncidentStatusEnum
    lot_name: Optional[str] = None
    camera_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class IncidentActionResponse(BaseModel):
    success: bool
    incident_id: int
    previous_status: IncidentStatusEnum
    new_status: IncidentStatusEnum
    message: str
    incident: IncidentResponse
