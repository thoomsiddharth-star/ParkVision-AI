from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    camera_number = Column(String(50), nullable=False)
    status = Column(String(50), default="DEMO", nullable=False)  # ONLINE, OFFLINE, DEGRADED, DEMO
    cars_detected = Column(Integer, default=0, nullable=False)
    spaces_detected = Column(Integer, default=0, nullable=False)
    ai_confidence = Column(Float, default=95.0, nullable=False)
    last_analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    stream_url = Column(String(255), nullable=True)

    # Relationships
    lot = relationship("ParkingLot", back_populates="cameras")
    incidents = relationship("Incident", back_populates="camera")
