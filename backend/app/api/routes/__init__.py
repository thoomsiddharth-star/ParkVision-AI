from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.admin_dashboard import router as admin_dashboard_router
from app.api.routes.locations import router as locations_router
from app.api.routes.floors import router as floors_router
from app.api.routes.zones import router as zones_router
from app.api.routes.spaces import router as spaces_router
from app.api.routes.reservations import router as reservations_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.simulation import router as simulation_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.lots import router as lots_router
from app.api.routes.navigation import router as navigation_router
from app.api.routes.insights import router as insights_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.driver import router as driver_router

api_router = APIRouter(prefix="/api")

# System & Auth
api_router.include_router(health_router)
api_router.include_router(auth_router)

# Smart Parking Platform Core
api_router.include_router(admin_dashboard_router)
api_router.include_router(locations_router)
api_router.include_router(floors_router)
api_router.include_router(zones_router)
api_router.include_router(spaces_router)
api_router.include_router(reservations_router)
api_router.include_router(notifications_router)
api_router.include_router(simulation_router)

# Analytics & Ancillary
api_router.include_router(analytics_router)
api_router.include_router(lots_router)
api_router.include_router(navigation_router)
api_router.include_router(insights_router)
api_router.include_router(incidents_router)
api_router.include_router(driver_router)

__all__ = ["api_router"]
