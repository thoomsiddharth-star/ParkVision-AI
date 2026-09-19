from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.parking_lot import ParkingLot
from app.models.parking_space import ParkingSpace
from app.models.parking_event import ParkingEvent

class ParkingService:
    @staticmethod
    def get_lots(db: Session) -> List[ParkingLot]:
        return db.query(ParkingLot).all()

    @staticmethod
    def get_lot_by_id(db: Session, lot_id: int) -> ParkingLot:
        lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "LOT_NOT_FOUND", "message": f"Parking lot with ID {lot_id} not found."}
            )
        return lot

    @staticmethod
    def get_spaces_by_lot(db: Session, lot_id: int) -> List[ParkingSpace]:
        # Verify lot exists
        ParkingService.get_lot_by_id(db, lot_id)
        return db.query(ParkingSpace).filter(ParkingSpace.parking_lot_id == lot_id).order_by(ParkingSpace.id).all()

    @staticmethod
    def get_space_by_id(db: Session, space_id: int) -> ParkingSpace:
        space = db.query(ParkingSpace).filter(ParkingSpace.id == space_id).first()
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "SPACE_NOT_FOUND", "message": f"Parking space with ID {space_id} not found."}
            )
        return space

    @staticmethod
    def select_space(db: Session, space_id: int, permanent_reservation: bool = False) -> Dict[str, Any]:
        space = ParkingService.get_space_by_id(db, space_id)

        if space.status == "OCCUPIED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "SPACE_OCCUPIED",
                    "message": f"Parking space {space.space_number} is currently occupied."
                }
            )

        if space.status == "RESERVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "SPACE_RESERVED",
                    "message": f"Parking space {space.space_number} is already reserved."
                }
            )

        # Selection of available space
        if permanent_reservation:
            prev_status = space.status
            space.status = "RESERVED"
            space.last_detected_at = datetime.utcnow()
            
            # Record event
            evt = ParkingEvent(
                parking_space_id=space.id,
                event_type="SPACE_RESERVED",
                previous_status=prev_status,
                new_status="RESERVED",
                timestamp=datetime.utcnow(),
                confidence=100.0
            )
            db.add(evt)
            ParkingService.recalculate_lot_stats(db, space.parking_lot_id)
            db.commit()
            db.refresh(space)

        return {
            "success": True,
            "space_id": space.id,
            "space_number": space.space_number,
            "status": space.status,
            "message": f"Parking space {space.space_number} selected successfully.",
            "space": space
        }

    @staticmethod
    def get_live_parking(db: Session, lot_id: Optional[int] = None) -> Dict[str, Any]:
        query = db.query(ParkingSpace)
        if lot_id:
            query = query.filter(ParkingSpace.parking_lot_id == lot_id)
        spaces = query.order_by(ParkingSpace.id).all()

        total = len(spaces)
        available = sum(1 for s in spaces if s.status == "AVAILABLE")
        occupied = sum(1 for s in spaces if s.status == "OCCUPIED")
        reserved = sum(1 for s in spaces if s.status == "RESERVED")
        occupancy_rate = round((occupied / total) * 100.0, 1) if total > 0 else 0.0

        return {
            "total_spaces": total,
            "available_spaces": available,
            "occupied_spaces": occupied,
            "reserved_spaces": reserved,
            "occupancy_percentage": occupancy_rate,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "spaces": spaces
        }

    @staticmethod
    def recalculate_lot_stats(db: Session, lot_id: int):
        lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
        if not lot:
            return

        spaces = db.query(ParkingSpace).filter(ParkingSpace.parking_lot_id == lot_id).all()
        total = len(spaces)
        occupied = sum(1 for s in spaces if s.status == "OCCUPIED")
        available = sum(1 for s in spaces if s.status == "AVAILABLE")
        reserved = sum(1 for s in spaces if s.status == "RESERVED")

        lot.capacity = total
        lot.occupied_spaces = occupied
        lot.available_spaces = available
        
        # Calculate active percentage
        non_reserved = total - reserved
        if non_reserved > 0:
            rate = round((occupied / non_reserved) * 100.0, 1)
        else:
            rate = 0.0
        lot.occupancy_percentage = min(100.0, max(0.0, rate))

        if lot.occupancy_percentage >= 95.0:
            lot.status = "FULL"
        elif lot.occupancy_percentage >= 75.0:
            lot.status = "HIGH"
        elif lot.occupancy_percentage >= 45.0:
            lot.status = "MODERATE"
        else:
            lot.status = "NORMAL"

        lot.updated_at = datetime.utcnow()
