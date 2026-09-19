from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class ParkingEvent(Base):
    __tablename__ = "parking_events"

    id = Column(Integer, primary_key=True, index=True)
    parking_space_id = Column(Integer, ForeignKey("parking_spaces.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # SPACE_OCCUPIED, SPACE_AVAILABLE, SPACE_RESERVED, VEHICLE_DETECTED, VEHICLE_LEFT
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    confidence = Column(Float, nullable=True)

    # Relationships
    space = relationship("ParkingSpace", back_populates="events")
