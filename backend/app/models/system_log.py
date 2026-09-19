from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database.database import Base

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=True)
    actor_name = Column(String(100), default="System", nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<SystemLog {self.action} on {self.entity_type}:{self.entity_id}>"
