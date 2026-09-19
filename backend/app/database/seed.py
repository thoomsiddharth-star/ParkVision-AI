from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.models.parking_lot import ParkingLot
from app.models.parking_space import ParkingSpace
from app.models.camera import Camera
from app.models.parking_event import ParkingEvent
from app.models.incident import Incident
from app.models.user import User
from app.core.config import settings
from app.core.security import hash_password

def seed_database(db: Session):
    # Check if already seeded
    if db.query(ParkingLot).first() is not None:
        return

    print("Seeding ParkVision AI database with realistic Indian city parking data...")

    # 1. Create Parking Lots
    lots_data = [
        {
            "name": "Central Mall Parking",
            "address": "450 MG Road, Central Commercial District, Bengaluru",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "capacity": 40,
            "price_per_hour": 50.0,
            "walking_time": "3 min",
            "status": "MODERATE",
            "cameras": [
                {"name": "North Gate Entrance Cam", "camera_number": "CAM-01", "status": "DEMO", "cars_detected": 14, "spaces_detected": 20, "ai_confidence": 97.2},
                {"name": "Main Floor Deck A Cam", "camera_number": "CAM-02", "status": "DEMO", "cars_detected": 14, "spaces_detected": 20, "ai_confidence": 96.8},
                {"name": "Main Floor Deck B Cam", "camera_number": "CAM-03", "status": "DEMO", "cars_detected": 12, "spaces_detected": 20, "ai_confidence": 98.1},
                {"name": "South Exit Bay Cam", "camera_number": "CAM-04", "status": "DEMO", "cars_detected": 8, "spaces_detected": 15, "ai_confidence": 95.4},
            ]
        },
        {
            "name": "City Center Parking",
            "address": "120 Residency Road, Financial Plaza, Bengaluru",
            "latitude": 12.9738,
            "longitude": 77.6012,
            "capacity": 42,
            "price_per_hour": 60.0,
            "walking_time": "5 min",
            "status": "HIGH",
            "cameras": [
                {"name": "Financial Plaza Entry Cam", "camera_number": "CAM-05", "status": "DEMO", "cars_detected": 18, "spaces_detected": 22, "ai_confidence": 96.4},
                {"name": "Tower A Basement Cam", "camera_number": "CAM-06", "status": "DEMO", "cars_detected": 16, "spaces_detected": 20, "ai_confidence": 97.0},
                {"name": "Tower B Basement Cam", "camera_number": "CAM-07", "status": "DEMO", "cars_detected": 15, "spaces_detected": 20, "ai_confidence": 95.9},
            ]
        },
        {
            "name": "Tech Park Parking",
            "address": "88 Silicon Boulevard, Outer Ring Road, Bengaluru",
            "latitude": 12.9249,
            "longitude": 77.6841,
            "capacity": 40,
            "price_per_hour": 30.0,
            "walking_time": "7 min",
            "status": "NORMAL",
            "cameras": [
                {"name": "Security Gate 1 Cam", "camera_number": "CAM-08", "status": "DEMO", "cars_detected": 9, "spaces_detected": 20, "ai_confidence": 98.4},
                {"name": "Innovation Deck North", "camera_number": "CAM-09", "status": "DEMO", "cars_detected": 10, "spaces_detected": 20, "ai_confidence": 97.9},
                {"name": "EV Fast Charging Station Cam", "camera_number": "CAM-10", "status": "DEMO", "cars_detected": 5, "spaces_detected": 8, "ai_confidence": 99.1},
                {"name": "Visitor Lot Cam", "camera_number": "CAM-11", "status": "DEMO", "cars_detected": 8, "spaces_detected": 15, "ai_confidence": 96.2},
            ]
        },
        {
            "name": "Metro Station Parking",
            "address": "15 Indiranagar Metro Station Rd, Bengaluru",
            "latitude": 12.9784,
            "longitude": 77.6408,
            "capacity": 50,
            "price_per_hour": 20.0,
            "walking_time": "2 min",
            "status": "MODERATE",
            "cameras": [
                {"name": "Metro Concourse Cam", "camera_number": "CAM-12", "status": "DEMO", "cars_detected": 17, "spaces_detected": 25, "ai_confidence": 96.7},
                {"name": "Platform 1 Access Cam", "camera_number": "CAM-13", "status": "DEMO", "cars_detected": 18, "spaces_detected": 25, "ai_confidence": 97.3},
                {"name": "Park & Ride Gate Cam", "camera_number": "CAM-14", "status": "DEMO", "cars_detected": 12, "spaces_detected": 20, "ai_confidence": 95.8},
            ]
        }
    ]

    # Specific initial available indices for Central Mall Parking (Lot 1)
    # Exactly 12 available and 28 occupied = 70% occupancy
    central_available_set = {1, 3, 5, 7, 9, 13, 17, 21, 25, 29, 33, 37}

    created_lots = []
    all_created_spaces = []
    created_cameras = []

    for lot_idx, l_data in enumerate(lots_data):
        cameras_data = l_data.pop("cameras")
        capacity = l_data["capacity"]

        lot = ParkingLot(
            name=l_data["name"],
            address=l_data["address"],
            latitude=l_data["latitude"],
            longitude=l_data["longitude"],
            capacity=capacity,
            price_per_hour=l_data["price_per_hour"],
            walking_time=l_data["walking_time"],
            status=l_data["status"],
            created_at=datetime.utcnow() - timedelta(days=30),
            updated_at=datetime.utcnow()
        )
        db.add(lot)
        db.flush()
        created_lots.append(lot)

        # Create Cameras for this lot
        for c_data in cameras_data:
            cam = Camera(
                parking_lot_id=lot.id,
                name=c_data["name"],
                camera_number=c_data["camera_number"],
                status=c_data["status"],
                cars_detected=c_data["cars_detected"],
                spaces_detected=c_data["spaces_detected"],
                ai_confidence=c_data["ai_confidence"],
                last_analyzed_at=datetime.utcnow(),
                stream_url=None  # Explicitly None for DEMO mode
            )
            db.add(cam)
            db.flush()
            created_cameras.append(cam)

        # Create Spaces for this lot
        lot_spaces = []
        occupied_count = 0
        available_count = 0
        reserved_count = 0

        prefix = "A" if lot_idx == 0 else ("B" if lot_idx == 1 else ("C" if lot_idx == 2 else "M"))

        for i in range(1, capacity + 1):
            space_num = f"{prefix}{i:02d}"

            # Space Type distribution
            if i in [1, 2, 3, 4]:
                space_type = "EV"
            elif i in [5, 6]:
                space_type = "ACCESSIBLE"
            elif i in [capacity - 1, capacity]:
                space_type = "RESERVED"
            else:
                space_type = "STANDARD"

            # Status determination
            if lot_idx == 0:
                # Lot 1 matches Central Mall exact 70% breakdown
                if space_type == "RESERVED":
                    status = "RESERVED"
                    confidence = 95.0
                    reserved_count += 1
                elif i in central_available_set:
                    status = "AVAILABLE"
                    confidence = None
                    available_count += 1
                else:
                    status = "OCCUPIED"
                    confidence = round(random.uniform(93.0, 98.5), 1)
                    occupied_count += 1
            else:
                # Other lots have realistic ratios
                if space_type == "RESERVED":
                    status = "RESERVED"
                    confidence = 94.0
                    reserved_count += 1
                elif lot_idx == 1:  # 81% occupancy
                    is_avail = i in [1, 5, 11, 15, 21, 27, 33, 39]
                    status = "AVAILABLE" if is_avail else "OCCUPIED"
                    confidence = None if is_avail else round(random.uniform(92.0, 98.0), 1)
                    if is_avail:
                        available_count += 1
                    else:
                        occupied_count += 1
                elif lot_idx == 2:  # 48% occupancy
                    is_avail = i % 2 != 0
                    status = "AVAILABLE" if is_avail else "OCCUPIED"
                    confidence = None if is_avail else round(random.uniform(94.0, 99.0), 1)
                    if is_avail:
                        available_count += 1
                    else:
                        occupied_count += 1
                else:  # Metro 70% occupancy
                    is_avail = i % 3 == 0
                    status = "AVAILABLE" if is_avail else "OCCUPIED"
                    confidence = None if is_avail else round(random.uniform(93.0, 98.0), 1)
                    if is_avail:
                        available_count += 1
                    else:
                        occupied_count += 1

            space = ParkingSpace(
                parking_lot_id=lot.id,
                space_number=space_num,
                status=status,
                space_type=space_type,
                latitude=lot.latitude + random.uniform(-0.0005, 0.0005),
                longitude=lot.longitude + random.uniform(-0.0005, 0.0005),
                confidence=confidence,
                last_detected_at=datetime.utcnow() - timedelta(seconds=random.randint(5, 300))
            )
            db.add(space)
            lot_spaces.append(space)
            all_created_spaces.append(space)

        db.flush()

        # Update lot counts
        lot.occupied_spaces = occupied_count
        lot.available_spaces = available_count
        total_active = capacity - reserved_count
        lot.occupancy_percentage = round((occupied_count / total_active) * 100.0, 1) if total_active > 0 else 0.0

        if lot.occupancy_percentage >= 95:
            lot.status = "FULL"
        elif lot.occupancy_percentage >= 75:
            lot.status = "HIGH"
        elif lot.occupancy_percentage >= 50:
            lot.status = "MODERATE"
        else:
            lot.status = "NORMAL"

    # 3. Create Seed Parking Events (for historical analytics and activity stream)
    now = datetime.utcnow()
    for space in all_created_spaces[:30]:
        # Events over the past few hours
        event_time = now - timedelta(minutes=random.randint(2, 240))
        event_type = "SPACE_OCCUPIED" if space.status == "OCCUPIED" else "SPACE_AVAILABLE"
        prev_status = "AVAILABLE" if event_type == "SPACE_OCCUPIED" else "OCCUPIED"

        evt = ParkingEvent(
            parking_space_id=space.id,
            event_type=event_type,
            previous_status=prev_status,
            new_status=space.status,
            timestamp=event_time,
            confidence=space.confidence or 96.0
        )
        db.add(evt)

    # 4. Create Seed Incidents
    seed_incidents = [
        {
            "parking_lot_id": created_lots[0].id,
            "camera_id": created_cameras[0].id,
            "type": "DOUBLE_PARKING",
            "severity": "MEDIUM",
            "description": "White SUV partially straddling spaces A04 and A05",
            "timestamp": now - timedelta(minutes=24),
            "status": "OPEN"
        },
        {
            "parking_lot_id": created_lots[0].id,
            "camera_id": created_cameras[1].id,
            "type": "OUTSIDE_SPACE",
            "severity": "LOW",
            "description": "Sedan parked 15cm outside marked yellow boundary line in A18",
            "timestamp": now - timedelta(minutes=72),
            "status": "REVIEWED"
        },
        {
            "parking_lot_id": created_lots[1].id,
            "camera_id": created_cameras[4].id,
            "type": "BLOCKED_EMERGENCY_LANE",
            "severity": "HIGH",
            "description": "Commercial delivery van blocking fire hydrant access lane",
            "timestamp": now - timedelta(hours=3),
            "status": "RESOLVED"
        },
        {
            "parking_lot_id": created_lots[2].id,
            "camera_id": created_cameras[8].id,
            "type": "UNAUTHORIZED_PARKING",
            "severity": "HIGH",
            "description": "Non-EV vehicle occupying designated fast charger bay C03",
            "timestamp": now - timedelta(minutes=45),
            "status": "OPEN"
        }
    ]

    for inc_data in seed_incidents:
        inc = Incident(**inc_data)
        db.add(inc)

    # 5. Create Seed Users
    if not db.query(User).filter(User.email == settings.ADMIN_EMAIL).first():
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            full_name="ParkVision System Administrator",
            role="ADMIN",
            is_active=True
        )
        db.add(admin_user)

    if not db.query(User).filter(User.email == "user@parkvision.ai").first():
        demo_user = User(
            email="user@parkvision.ai",
            hashed_password=hash_password("user123"),
            full_name="Demo Driver",
            role="USER",
            is_active=True
        )
        db.add(demo_user)

    db.commit()
    print("Database seeding completed successfully with 4 lots, 172 spaces, cameras, events, incidents, and accounts.")
