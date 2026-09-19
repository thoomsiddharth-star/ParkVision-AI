import asyncio
import random
import logging
from datetime import datetime, timezone
from app.database.database import SessionLocal
from app.models.parking_space import ParkingSpace
from app.models.system_log import SystemLog
from app.services.websocket_manager import ws_manager
from app.core.config import settings

logger = logging.getLogger("parkvision.simulation")

class SimulationService:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.task: asyncio.Task = None

    async def start(self):
        if self.is_running:
            self.is_paused = False
            return
        self.is_running = True
        self.is_paused = False
        self.task = asyncio.create_task(self._run_loop())
        logger.info("Smart parking demo simulation engine started.")

    async def pause(self):
        self.is_paused = True
        logger.info("Smart parking demo simulation engine paused.")

    async def resume(self):
        self.is_paused = False
        logger.info("Smart parking demo simulation engine resumed.")

    async def stop(self):
        self.is_running = False
        self.is_paused = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Smart parking demo simulation engine stopped.")

    async def _run_loop(self):
        while self.is_running:
            try:
                interval = getattr(settings, "SIMULATION_INTERVAL_SECONDS", 4)
                await asyncio.sleep(interval)
                if not self.is_paused and self.is_running:
                    await self.step_simulation()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in demo simulation step: {e}", exc_info=True)
                await asyncio.sleep(2)

    async def step_simulation(self):
        db = SessionLocal()
        try:
            # Query active spaces (not Blocked)
            spaces = db.query(ParkingSpace).filter(
                ParkingSpace.status != "Blocked"
            ).all()

            if not spaces:
                return

            # Pick 1 or 2 spaces at random
            count_to_toggle = 1 if random.random() > 0.35 else 2
            chosen_spaces = random.sample(spaces, min(count_to_toggle, len(spaces)))

            for space in chosen_spaces:
                old_status = space.status
                dice = random.random()

                if old_status == "Available":
                    new_status = "Occupied" if dice > 0.15 else "Reserved"
                elif old_status == "Occupied":
                    new_status = "Available"
                elif old_status == "Reserved":
                    new_status = "Occupied" if dice > 0.5 else "Available"
                else:
                    new_status = "Available"

                space.status = new_status
                db.flush()

                # Add system log entry
                log = SystemLog(
                    actor_id=None,
                    actor_name="Demo Simulation",
                    action="SIMULATION_STATUS_CHANGE",
                    entity_type="ParkingSpace",
                    entity_id=str(space.id),
                    description=f"Demo simulation changed space '{space.space_code}' from '{old_status}' to '{new_status}'"
                )
                db.add(log)

                # Broadcast via WebSocket
                await ws_manager.broadcast_space_update(
                    space_id=space.id,
                    space_number=space.space_code,
                    status=new_status
                )

            db.commit()

        except Exception as e:
            logger.error(f"Failed to step simulation: {e}")
            db.rollback()
        finally:
            db.close()

simulation_service = SimulationService()
