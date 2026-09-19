from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, default=40, nullable=False)
    occupied_spaces = Column(Integer, default=0, nullable=False)
    available_spaces = Column(Integer, default=40, nullable=False)
    occupancy_percentage = Column(Float, default=0.0, nullable=False)
    price_per_hour = Column(Float, default=40.0, nullable=False)
    walking_time = Column(String(50), default="5 min", nullable=False)
    status = Column(String(50), default="NORMAL", nullable=False)  # NORMAL, MODERATE, HIGH, FULL
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    spaces = relationship("ParkingSpace", back_populates="lot", cascade="all, delete-orphan")
    cameras = relationship("Camera", back_populates="lot", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="lot", cascade="all, delete-orphan")
