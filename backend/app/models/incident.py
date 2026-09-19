from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # WRONG_WAY, DOUBLE_PARKING, OUTSIDE_SPACE, BLOCKED_EMERGENCY_LANE, LONG_TERM_PARKING, UNAUTHORIZED_PARKING
    severity = Column(String(20), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH
    description = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(String(20), default="OPEN", nullable=False)  # OPEN, REVIEWED, RESOLVED

    # Relationships
    lot = relationship("ParkingLot", back_populates="incidents")
