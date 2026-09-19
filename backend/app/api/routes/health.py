from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Backend & Database Health Check")
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "ai_mode": settings.AI_MODE
    }
