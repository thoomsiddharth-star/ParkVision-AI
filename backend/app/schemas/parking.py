from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SpaceStatusEnum(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"

class SpaceTypeEnum(str, Enum):
    STANDARD = "STANDARD"
    EV = "EV"
    ACCESSIBLE = "ACCESSIBLE"
    RESERVED = "RESERVED"

class ParkingSpaceBase(BaseModel):
    parking_lot_id: int = Field(..., gt=0)
    space_number: str = Field(..., min_length=1, max_length=20)
    status: SpaceStatusEnum = Field(default=SpaceStatusEnum.AVAILABLE)
    space_type: SpaceTypeEnum = Field(default=SpaceTypeEnum.STANDARD)
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=100.0)

class ParkingSpaceResponse(ParkingSpaceBase):
    id: int
    last_detected_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SpaceSelectRequest(BaseModel):
    permanent_reservation: bool = Field(default=False, description="Whether to permanently reserve the space")
    user_id: Optional[str] = Field(default=None, description="Optional driver user ID")

class SpaceSelectResponse(BaseModel):
    success: bool
    space_id: int
    space_number: str
    status: SpaceStatusEnum
    message: str
    space: Optional[ParkingSpaceResponse] = None

class LiveParkingResponse(BaseModel):
    total_spaces: int
    available_spaces: int
    occupied_spaces: int
    reserved_spaces: int
    occupancy_percentage: float
    last_updated: str
    spaces: List[ParkingSpaceResponse] = []

class WebSocketParkingUpdate(BaseModel):
    type: str = "parking_update"
    space_id: int
    space_number: str
    previous_status: SpaceStatusEnum
    status: SpaceStatusEnum
    timestamp: str
    confidence: Optional[float] = None
    vehicle_type: Optional[str] = None
