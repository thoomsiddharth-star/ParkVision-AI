from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class Floor(Base):
    __tablename__ = "floors"

    id = Column(Integer, primary_key=True, index=True)
    parking_location_id = Column(Integer, ForeignKey("parking_locations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    floor_number = Column(Integer, default=0, nullable=False)
    floor_plan_url = Column(String(500), nullable=True)
    floor_plan_width = Column(Integer, nullable=True)
    floor_plan_height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    parking_location = relationship("ParkingLocation", back_populates="floors")
    zones = relationship("Zone", back_populates="floor", cascade="all, delete-orphan")
    spaces = relationship("ParkingSpace", back_populates="floor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Floor {self.name} (Loc: {self.parking_location_id})>"
