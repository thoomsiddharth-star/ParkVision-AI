from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class ParkingSpace(Base):
    __tablename__ = "parking_spaces"

    id = Column(Integer, primary_key=True, index=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=True, index=True)
    floor_id = Column(Integer, ForeignKey("floors.id", ondelete="CASCADE"), nullable=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    
    space_code = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    
    # Types: Normal, Disabled, EV, VIP, Reserved
    type = Column(String(50), default="Normal", nullable=False)
    
    # Statuses: Available, Occupied, Reserved, Blocked
    status = Column(String(50), default="Available", nullable=False, index=True)
    
    # Normalized coordinates relative to floor plan image (0.0 to 1.0)
    x = Column(Float, default=0.0, nullable=False)
    y = Column(Float, default=0.0, nullable=False)
    width = Column(Float, default=0.08, nullable=False)
    height = Column(Float, default=0.05, nullable=False)
    rotation = Column(Float, default=0.0, nullable=False)
    
    price = Column(Float, default=30.0, nullable=False)
    notes = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Compatibility attributes
    @property
    def space_number(self):
        return self.space_code

    @space_number.setter
    def space_number(self, value):
        self.space_code = value

    @property
    def space_type(self):
        return self.type

    @space_type.setter
    def space_type(self, value):
        self.type = value

    # Relationships
    lot = relationship("ParkingLot", back_populates="spaces")
    floor = relationship("Floor", back_populates="spaces")
    zone = relationship("Zone", back_populates="spaces")
    reservations = relationship("Reservation", back_populates="space", cascade="all, delete-orphan")
    events = relationship("ParkingEvent", back_populates="space", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ParkingSpace {self.space_code} ({self.status})>"
