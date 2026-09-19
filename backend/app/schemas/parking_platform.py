from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ==========================================
# Parking Location Schemas
# ==========================================
class LocationBase(BaseModel):
    name: str = Field(..., example="ParkVision Central Parking")
    address: Optional[str] = Field(None, example="Hyderabad, Telangana")
    latitude: Optional[float] = Field(None, example=17.3850)
    longitude: Optional[float] = Field(None, example=78.4867)
    description: Optional[str] = Field(None, example="Multi-level smart parking facility with 4 floors")
    operating_hours: Optional[str] = Field("24/7", example="24/7")
    pricing: Optional[str] = Field("₹30/hour", example="₹30/hour")
    status: Optional[str] = Field("Open", example="Open")

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    operating_hours: Optional[str] = None
    pricing: Optional[str] = None
    status: Optional[str] = None

class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    floor_count: int = 0
    total_spaces: int = 0
    available_spaces: int = 0
    occupied_spaces: int = 0
    reserved_spaces: int = 0
    blocked_spaces: int = 0
    occupancy_rate: float = 0.0

    class Config:
        from_attributes = True

# ==========================================
# Floor Schemas
# ==========================================
class FloorBase(BaseModel):
    name: str = Field(..., example="Ground Floor")
    floor_number: int = Field(0, example=0)
    floor_plan_url: Optional[str] = None
    floor_plan_width: Optional[int] = None
    floor_plan_height: Optional[int] = None

class FloorCreate(FloorBase):
    parking_location_id: int

class FloorUpdate(BaseModel):
    name: Optional[str] = None
    floor_number: Optional[int] = None
    floor_plan_url: Optional[str] = None
    floor_plan_width: Optional[int] = None
    floor_plan_height: Optional[int] = None

class FloorResponse(FloorBase):
    id: int
    parking_location_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_spaces: int = 0
    available_spaces: int = 0
    occupied_spaces: int = 0
    reserved_spaces: int = 0
    blocked_spaces: int = 0
    occupancy_rate: float = 0.0

    class Config:
        from_attributes = True

# ==========================================
# Zone Schemas
# ==========================================
class ZoneBase(BaseModel):
    name: str = Field(..., example="Zone A")
    description: Optional[str] = Field(None, example="North Wing - EV & VIP")

class ZoneCreate(ZoneBase):
    floor_id: int

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ZoneResponse(ZoneBase):
    id: int
    floor_id: int
    created_at: datetime
    total_spaces: int = 0

    class Config:
        from_attributes = True

# ==========================================
# Parking Space Schemas
# ==========================================
class ParkingSpaceBase(BaseModel):
    space_code: str = Field(..., example="P001")
    name: Optional[str] = Field(None, example="Spot P001")
    type: str = Field("Normal", example="Normal")  # Normal, Disabled, EV, VIP, Reserved
    status: str = Field("Available", example="Available")  # Available, Occupied, Reserved, Blocked
    x: float = Field(..., ge=0.0, le=1.0, example=0.25)
    y: float = Field(..., ge=0.0, le=1.0, example=0.40)
    width: float = Field(0.08, ge=0.001, le=1.0, example=0.08)
    height: float = Field(0.05, ge=0.001, le=1.0, example=0.05)
    rotation: float = Field(0.0, example=0.0)
    price: float = Field(30.0, example=30.0)
    notes: Optional[str] = None

class ParkingSpaceCreate(ParkingSpaceBase):
    floor_id: int
    zone_id: Optional[int] = None

class ParkingSpaceUpdate(BaseModel):
    space_code: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    floor_id: Optional[int] = None
    zone_id: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    rotation: Optional[float] = None
    price: Optional[float] = None
    notes: Optional[str] = None

class ParkingSpaceBatchItem(BaseModel):
    id: Optional[int] = None
    space_code: str
    name: Optional[str] = None
    type: str = "Normal"
    status: str = "Available"
    zone_id: Optional[int] = None
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0
    price: float = 30.0
    notes: Optional[str] = None

class ParkingSpaceBatchRequest(BaseModel):
    floor_id: int
    spaces: List[ParkingSpaceBatchItem]

class ParkingSpaceStatusUpdate(BaseModel):
    status: str = Field(..., example="Occupied")  # Available, Occupied, Reserved, Blocked

class ParkingSpaceResponse(ParkingSpaceBase):
    id: int
    floor_id: Optional[int]
    zone_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime] = None
    zone_name: Optional[str] = None
    floor_name: Optional[str] = None

    class Config:
        from_attributes = True

# ==========================================
# Reservation Schemas
# ==========================================
class ReservationCreate(BaseModel):
    parking_space_id: int
    start_time: datetime
    end_time: datetime

class ReservationStatusUpdate(BaseModel):
    status: str  # Upcoming, Active, Completed, Cancelled

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    parking_space_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    space_code: Optional[str] = None
    floor_name: Optional[str] = None
    location_name: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    price: Optional[float] = None

    class Config:
        from_attributes = True

# ==========================================
# System Log & Notification Schemas
# ==========================================
class SystemLogResponse(BaseModel):
    id: int
    actor_id: Optional[int] = None
    actor_name: Optional[str] = "System"
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    type: str
    message: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# User Management Schemas
# ==========================================
class UserAdminResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    role: str
    status: str
    is_active: bool
    reservations_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class UserStatusUpdate(BaseModel):
    status: str  # Active, Disabled

# ==========================================
# Dashboard & Analytics Schemas
# ==========================================
class FloorComparisonItem(BaseModel):
    floor_id: int
    floor_name: str
    floor_number: int
    total_spaces: int
    available_spaces: int
    occupied_spaces: int
    reserved_spaces: int
    blocked_spaces: int
    occupancy_rate: float

class AdminDashboardMetrics(BaseModel):
    total_spaces: int
    available_spaces: int
    occupied_spaces: int
    reserved_spaces: int
    blocked_spaces: int
    occupancy_rate: float
    total_locations: int
    total_floors: int
    active_reservations: int
    floors_comparison: List[FloorComparisonItem]
    recent_activity: List[SystemLogResponse]
