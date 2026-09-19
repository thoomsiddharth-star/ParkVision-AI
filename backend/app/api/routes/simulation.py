from fastapi import APIRouter
from app.services.simulation_service import simulation_service

router = APIRouter(prefix="/simulation", tags=["Demo Simulation"])

@router.post("/start")
async def start_simulation():
    await simulation_service.start()
    return {"status": "started", "is_running": simulation_service.is_running, "is_paused": simulation_service.is_paused}

@router.post("/pause")
async def pause_simulation():
    await simulation_service.pause()
    return {"status": "paused", "is_running": simulation_service.is_running, "is_paused": simulation_service.is_paused}

@router.post("/resume")
async def resume_simulation():
    await simulation_service.resume()
    return {"status": "resumed", "is_running": simulation_service.is_running, "is_paused": simulation_service.is_paused}

@router.post("/stop")
async def stop_simulation():
    await simulation_service.stop()
    return {"status": "stopped", "is_running": simulation_service.is_running, "is_paused": simulation_service.is_paused}

@router.get("/status")
def get_simulation_status():
    return {
        "is_running": simulation_service.is_running,
        "is_paused": simulation_service.is_paused
    }
