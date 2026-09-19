from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class LotStatusEnum(str, Enum):
    NORMAL = "NORMAL"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    FULL = "FULL"

class ParkingLotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=255)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    capacity: int = Field(..., ge=0)
    occupied_spaces: int = Field(default=0, ge=0)
    available_spaces: int = Field(default=0, ge=0)
    occupancy_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    price_per_hour: float = Field(default=40.0, ge=0.0)
    walking_time: str = Field(default="5 min")
    status: LotStatusEnum = Field(default=LotStatusEnum.NORMAL)

class ParkingLotCreate(ParkingLotBase):
    pass

class ParkingLotResponse(ParkingLotBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ParkingLotDetailResponse(ParkingLotResponse):
    pass
