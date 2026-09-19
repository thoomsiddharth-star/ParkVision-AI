from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.parking import router as parking_router
from app.api.routes.lots import router as lots_router
from app.api.routes.cameras import router as cameras_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.navigation import router as navigation_router
from app.api.routes.insights import router as insights_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.driver import router as driver_router
from app.api.routes.auth import router as auth_router
from app.api.routes.admin import router as admin_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(parking_router)
api_router.include_router(lots_router)
api_router.include_router(cameras_router)
api_router.include_router(analytics_router)
api_router.include_router(navigation_router)
api_router.include_router(insights_router)
api_router.include_router(incidents_router)
api_router.include_router(driver_router)

__all__ = ["api_router"]
