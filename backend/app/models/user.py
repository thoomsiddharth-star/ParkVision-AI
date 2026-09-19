from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="USER", nullable=False)  # "USER", "ADMIN", "SUPER_ADMIN"
    status = Column(String, default="Active", nullable=False)  # "Active", "Disabled"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def full_name(self):
        return self.name

    @full_name.setter
    def full_name(self, value):
        self.name = value

    @property
    def hashed_password(self):
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value):
        self.password_hash = value

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
