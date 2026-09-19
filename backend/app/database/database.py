import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# Determine database URL and connect args
connect_args = {}
database_url = settings.DATABASE_URL

if database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

try:
    engine = create_engine(database_url, connect_args=connect_args)
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    # Graceful fallback to local SQLite if PostgreSQL or configured URL fails
    fallback_url = "sqlite:///./parkvision.db"
    print(f"Warning: Failed to connect to {database_url} ({e}). Falling back to {fallback_url}")
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import app.models  # Ensure models are imported
    Base.metadata.create_all(bind=engine)
