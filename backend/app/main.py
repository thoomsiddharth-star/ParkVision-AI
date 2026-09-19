from contextlib import asynccontextmanager
import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.database.database import init_db, SessionLocal
from app.database.seed import seed_database
from app.api.routes import api_router
from app.services.websocket_manager import ws_manager
from app.services.simulation_service import simulation_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("parkvision.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing ParkVision AI Database...")
    init_db()

    # Automatically seed data if database is empty
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # Start Demo Simulation if AI_MODE is demo
    if settings.AI_MODE.lower() == "demo":
        logger.info("Starting background demo simulation engine...")
        await simulation_service.start()

    yield

    # Shutdown
    logger.info("Shutting down ParkVision AI...")
    if simulation_service.is_running:
        await simulation_service.stop()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "ParkVision AI — Camera-based intelligent smart parking management platform. "
        "Provides real-time occupancy tracking, AI vision simulation, parking recommendations, "
        "driver mode search, navigation, Recharts-ready analytics, and security incidents."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# -------------------------------------------------------------
# CORS Middleware Configuration
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Standardized Error Handling
# -------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Detail can be a dict with code/message or a plain string
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "ERROR")
        message = exc.detail.get("message", "An error occurred.")
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_msg = errors[0].get("msg") if errors else "Invalid request data."
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": first_msg,
                "details": errors
            }
        }
    )

# -------------------------------------------------------------
# WebSocket Endpoint: /ws/parking
# -------------------------------------------------------------
@app.websocket("/ws/parking")
async def websocket_parking_endpoint(websocket: WebSocket):
    """
    WebSocket feed for live parking updates. Broadcasts space occupancy changes
    and telemetry in real time.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keepalive listener / echo
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

# -------------------------------------------------------------
# Mount REST API Routes under /api
# -------------------------------------------------------------
app.include_router(api_router)

# -------------------------------------------------------------
# Static Frontend Serving (Directly supports existing web app)
# -------------------------------------------------------------
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
index_file = os.path.join(frontend_dir, "index.html")
js_dir = os.path.join(frontend_dir, "js")
styles_file = os.path.join(frontend_dir, "styles.css")
uploads_dir = os.path.join(frontend_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

if os.path.isdir(js_dir):
    app.mount("/js", StaticFiles(directory=js_dir), name="js")

if os.path.isdir(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/styles.css", include_in_schema=False)
def serve_styles():
    if os.path.isfile(styles_file):
        return FileResponse(styles_file, media_type="text/css")
    raise HTTPException(status_code=404, detail="styles.css not found")

@app.get("/admin-login", include_in_schema=False)
@app.get("/admin-login.html", include_in_schema=False)
def serve_admin_login():
    admin_login_path = os.path.join(frontend_dir, "admin-login.html")
    if os.path.isfile(admin_login_path):
        return FileResponse(admin_login_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="admin-login.html not found")

@app.get("/admin-dashboard", include_in_schema=False)
@app.get("/admin-dashboard.html", include_in_schema=False)
def serve_admin_dashboard():
    admin_dash_path = os.path.join(frontend_dir, "admin-dashboard.html")
    if os.path.isfile(admin_dash_path):
        return FileResponse(admin_dash_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="admin-dashboard.html not found")

@app.get("/", include_in_schema=False)
def serve_index():
    if os.path.isfile(index_file):
        return FileResponse(index_file, media_type="text/html")
    return {"message": "ParkVision AI API is running. Visit /docs for API documentation."}
