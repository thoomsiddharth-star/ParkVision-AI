from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class ParkingSpace(Base):
    __tablename__ = "parking_spaces"

    id = Column(Integer, primary_key=True, index=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False, index=True)
    space_number = Column(String(20), nullable=False, index=True)
    status = Column(String(50), default="AVAILABLE", nullable=False)  # AVAILABLE, OCCUPIED, RESERVED
    space_type = Column(String(50), default="STANDARD", nullable=False)  # STANDARD, EV, ACCESSIBLE, RESERVED
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    last_detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    lot = relationship("ParkingLot", back_populates="spaces")
    events = relationship("ParkingEvent", back_populates="space", cascade="all, delete-orphan")
