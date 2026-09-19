from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class CameraStatusEnum(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    DEMO = "DEMO"

class CameraBase(BaseModel):
    parking_lot_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    camera_number: str = Field(..., min_length=1, max_length=50)
    status: CameraStatusEnum = Field(default=CameraStatusEnum.DEMO)
    cars_detected: int = Field(default=0, ge=0)
    spaces_detected: int = Field(default=0, ge=0)
    ai_confidence: float = Field(default=95.0, ge=0.0, le=100.0)
    stream_url: Optional[str] = None

class CameraResponse(CameraBase):
    id: int
    last_analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CameraStatusResponse(BaseModel):
    id: int
    name: str
    camera_number: str
    status: CameraStatusEnum
    cars_detected: int
    spaces_detected: int
    ai_confidence: float
    last_analyzed_at: datetime
    stream_url: Optional[str] = None
    fps: int = 30
    latency_ms: int = 14
    resolution: str = "1080p"
    mode: str = "DEMO MODE — Simulated detection feed"
