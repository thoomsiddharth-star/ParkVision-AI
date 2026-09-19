from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class ParkingLocation(Base):
    __tablename__ = "parking_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    description = Column(String(500), nullable=True)
    operating_hours = Column(String(100), default="24/7", nullable=True)
    pricing = Column(String(100), default="₹30/hour", nullable=True)
    status = Column(String(50), default="Open", nullable=False)  # Open, Closed, Maintenance
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    floors = relationship("Floor", back_populates="parking_location", cascade="all, delete-orphan", order_by="Floor.floor_number")

    def __repr__(self):
        return f"<ParkingLocation {self.name}>"
