from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parking_space_id = Column(Integer, ForeignKey("parking_spaces.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="Upcoming", nullable=False)  # Upcoming, Active, Completed, Cancelled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User")
    space = relationship("ParkingSpace", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation #{self.id} Space:{self.parking_space_id} User:{self.user_id} ({self.status})>"
