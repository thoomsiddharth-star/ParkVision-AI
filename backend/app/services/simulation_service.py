import asyncio
import random
import logging
from datetime import datetime
from app.database.database import SessionLocal
from app.models.parking_lot import ParkingLot
from app.models.parking_space import ParkingSpace
from app.models.parking_event import ParkingEvent
from app.services.parking_service import ParkingService
from app.services.websocket_manager import ws_manager
from app.core.config import settings

logger = logging.getLogger("parkvision.simulation")

class SimulationService:
    def __init__(self):
        self.is_running = False
        self.task: asyncio.Task = None

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.task = asyncio.create_task(self._run_loop())
        logger.info("Demo simulation engine started.")

    async def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Demo simulation engine stopped.")

    async def _run_loop(self):
        while self.is_running:
            try:
                await asyncio.sleep(settings.SIMULATION_INTERVAL_SECONDS)
                await self.step_simulation()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in demo simulation step: {e}", exc_info=True)
                await asyncio.sleep(2)

    async def step_simulation(self):
        db = SessionLocal()
        try:
            # Focus primarily on Central Mall Parking (Lot 1) for immediate visual correlation
            # but occasionally pick from other lots
            target_lot_id = 1
            if random.random() > 0.8:
                lots = db.query(ParkingLot.id).all()
                if lots:
                    target_lot_id = random.choice(lots)[0]

            spaces = db.query(ParkingSpace).filter(
                ParkingSpace.parking_lot_id == target_lot_id,
                ParkingSpace.status != "RESERVED"  # Keep reserved bays stable
            ).all()

            if not spaces:
                return

            # Toggle 1 space (or occasionally 2) for realistic activity
            count_to_toggle = 1 if random.random() > 0.35 else 2
            chosen_spaces = random.sample(spaces, min(count_to_toggle, len(spaces)))

            for space in chosen_spaces:
                old_status = space.status
                vehicle_type = None

                if old_status == "AVAILABLE":
                    new_status = "OCCUPIED"
                    confidence = round(random.uniform(93.0, 98.8), 1)
                    vehicle_type = random.choice(["White Sedan", "Dark SUV", "Silver Hatchback", "Electric Compact"])
                    event_type = "SPACE_OCCUPIED"
                else:
                    new_status = "AVAILABLE"
                    confidence = None
                    event_type = "SPACE_AVAILABLE"

                space.status = new_status
                space.confidence = confidence
                space.last_detected_at = datetime.utcnow()

                # Add event record
                evt = ParkingEvent(
                    parking_space_id=space.id,
                    event_type=event_type,
                    previous_status=old_status,
                    new_status=new_status,
                    timestamp=datetime.utcnow(),
                    confidence=confidence or 95.0
                )
                db.add(evt)

                # Broadcast via WebSocket
                iso_ts = datetime.utcnow().isoformat() + "Z"
                payload = {
                    "type": "parking_update",
                    "space_id": space.id,
                    "space_number": space.space_number,
                    "previous_status": old_status,
                    "status": new_status,
                    "timestamp": iso_ts,
                    "confidence": confidence,
                    "vehicle_type": vehicle_type,
                    "lot_id": space.parking_lot_id
                }
                await ws_manager.broadcast(payload)

            # Recalculate parking lot occupancy statistics
            ParkingService.recalculate_lot_stats(db, target_lot_id)
            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to execute simulation step: {e}")
        finally:
            db.close()

simulation_service = SimulationService()
