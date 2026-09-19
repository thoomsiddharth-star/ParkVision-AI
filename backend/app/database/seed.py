from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.parking_location import ParkingLocation
from app.models.floor import Floor
from app.models.zone import Zone
from app.models.parking_space import ParkingSpace
from app.models.reservation import Reservation
from app.models.user import User
from app.models.system_log import SystemLog
from app.models.notification import Notification
from app.core.config import settings
from app.core.security import hash_password

def seed_database(db: Session):
    # 1. Seed Users (Admin and Demo User)
    admin_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin_user:
        admin_user = User(
            name="ParkVision Administrator",
            email=settings.ADMIN_EMAIL,
            phone="+91 98765 00001",
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role="ADMIN",
            status="Active",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Seeded Admin: {settings.ADMIN_EMAIL}")

    demo_user = db.query(User).filter(User.email == "user@parkvision.ai").first()
    if not demo_user:
        demo_user = User(
            name="Rahul Sharma",
            email="user@parkvision.ai",
            phone="+91 98765 12345",
            password_hash=hash_password("user123"),
            role="USER",
            status="Active",
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print("Seeded Demo User: user@parkvision.ai")

    # 2. Check if Parking Locations already seeded
    existing_loc = db.query(ParkingLocation).first()
    if existing_loc is not None:
        return

    print("Seeding Smart Parking Platform data (Locations, Floors, Floor Plans, Zones, Spaces)...")

    # 3. Create Main Parking Location (ParkVision Central Parking, Hyderabad)
    central_loc = ParkingLocation(
        name="ParkVision Central Parking",
        address="HITEC City, Madhapur, Hyderabad, Telangana",
        latitude=17.4435,
        longitude=78.3772,
        description="State-of-the-art multi-level smart parking facility with 4 floors, automated guidance, and EV fast chargers.",
        operating_hours="24/7",
        pricing="₹30/hour",
        status="Open"
    )
    db.add(central_loc)
    db.commit()
    db.refresh(central_loc)

    # 4. Create Floors
    floors_data = [
        {"name": "Basement", "floor_number": -1, "url": None},
        {"name": "Ground Floor", "floor_number": 0, "url": "/uploads/ground_floor_blueprint.svg"},
        {"name": "First Floor", "floor_number": 1, "url": None},
        {"name": "Second Floor", "floor_number": 2, "url": None},
    ]

    floors_map = {}
    for f_info in floors_data:
        floor = Floor(
            parking_location_id=central_loc.id,
            name=f_info["name"],
            floor_number=f_info["floor_number"],
            floor_plan_url=f_info["url"],
            floor_plan_width=1200,
            floor_plan_height=800
        )
        db.add(floor)
        db.flush()
        floors_map[f_info["name"]] = floor

    ground_floor = floors_map["Ground Floor"]

    # 5. Create Zones on Ground Floor
    zone_a = Zone(floor_id=ground_floor.id, name="Zone A", description="North Wing - EV & VIP")
    zone_b = Zone(floor_id=ground_floor.id, name="Zone B", description="Central Wing - General")
    zone_c = Zone(floor_id=ground_floor.id, name="Zone C", description="South Wing - Accessible & Standard")
    db.add_all([zone_a, zone_b, zone_c])
    db.commit()
    db.refresh(zone_a)
    db.refresh(zone_b)
    db.refresh(zone_c)

    # 6. Seed 20 Parking Spaces on Ground Floor with Normalized Coordinates [0.0 - 1.0]
    # Blueprint dimensions: 1200 x 800.
    # North Row Upper (y: 80-180 -> norm_y: ~0.11, height: 100/800 = 0.125, width: 60/1200 = 0.05)
    # North Row Lower (y: 210-310 -> norm_y: ~0.28, height: 100/800 = 0.125)
    # South Row Upper (y: 490-590 -> norm_y: ~0.62)
    # South Row Lower (y: 620-720 -> norm_y: ~0.78)

    spaces_seed = [
        # Zone A: Spaces P001 - P006 (North Upper)
        {"code": "P001", "name": "Spot P001", "zone": zone_a, "type": "EV", "status": "Available", "x": 0.195, "y": 0.11, "w": 0.055, "h": 0.115, "price": 40.0, "notes": "Level 2 EV Fast Charger"},
        {"code": "P002", "name": "Spot P002", "zone": zone_a, "type": "EV", "status": "Occupied", "x": 0.265, "y": 0.11, "w": 0.055, "h": 0.115, "price": 40.0, "notes": "Level 2 EV Fast Charger"},
        {"code": "P003", "name": "Spot P003", "zone": zone_a, "type": "VIP", "status": "Available", "x": 0.330, "y": 0.11, "w": 0.055, "h": 0.115, "price": 50.0, "notes": "VIP Reserved near Lobby"},
        {"code": "P004", "name": "Spot P004", "zone": zone_a, "type": "VIP", "status": "Occupied", "x": 0.398, "y": 0.11, "w": 0.055, "h": 0.115, "price": 50.0, "notes": "VIP Executive Bay"},
        {"code": "P005", "name": "Spot P005", "zone": zone_a, "type": "Normal", "status": "Available", "x": 0.465, "y": 0.11, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "Standard Wide Bay"},
        {"code": "P006", "name": "Spot P006", "zone": zone_a, "type": "Normal", "status": "Occupied", "x": 0.530, "y": 0.11, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "Standard Bay"},

        # Zone B: Spaces P007 - P012 (North Lower)
        {"code": "P007", "name": "Spot P007", "zone": zone_b, "type": "Normal", "status": "Available", "x": 0.195, "y": 0.275, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "Near West Driveway"},
        {"code": "P008", "name": "Spot P008", "zone": zone_b, "type": "Normal", "status": "Available", "x": 0.265, "y": 0.275, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "Central North Bay"},
        {"code": "P009", "name": "Spot P009", "zone": zone_b, "type": "Normal", "status": "Occupied", "x": 0.330, "y": 0.275, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "Central North Bay"},
        {"code": "P010", "name": "Spot P010", "zone": zone_b, "type": "Normal", "status": "Reserved", "x": 0.398, "y": 0.275, "w": 0.055, "h": 0.115, "price": 35.0, "notes": "Advance Reservation"},
        {"code": "P011", "name": "Spot P011", "zone": zone_b, "type": "Normal", "status": "Blocked", "x": 0.465, "y": 0.275, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "Maintenance bay"},
        {"code": "P012", "name": "Spot P012", "zone": zone_b, "type": "Normal", "status": "Available", "x": 0.530, "y": 0.275, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "Standard Bay"},

        # Zone C: Spaces P013 - P020 (South Aisles)
        {"code": "P013", "name": "Spot P013", "zone": zone_c, "type": "Disabled", "status": "Available", "x": 0.195, "y": 0.625, "w": 0.055, "h": 0.115, "price": 25.0, "notes": "Accessible Parking Bay"},
        {"code": "P014", "name": "Spot P014", "zone": zone_c, "type": "Disabled", "status": "Available", "x": 0.265, "y": 0.625, "w": 0.055, "h": 0.115, "price": 25.0, "notes": "Accessible Parking Bay"},
        {"code": "P015", "name": "Spot P015", "zone": zone_c, "type": "Normal", "status": "Occupied", "x": 0.330, "y": 0.625, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "South Main Bay"},
        {"code": "P016", "name": "Spot P016", "zone": zone_c, "type": "Normal", "status": "Available", "x": 0.398, "y": 0.625, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "South Main Bay"},
        {"code": "P017", "name": "Spot P017", "zone": zone_c, "type": "Normal", "status": "Available", "x": 0.195, "y": 0.785, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "South Lower Bay"},
        {"code": "P018", "name": "Spot P018", "zone": zone_c, "type": "Normal", "status": "Occupied", "x": 0.265, "y": 0.785, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "South Lower Bay"},
        {"code": "P019", "name": "Spot P019", "zone": zone_c, "type": "Normal", "status": "Available", "x": 0.330, "y": 0.785, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "South Lower Bay"},
        {"code": "P020", "name": "Spot P020", "zone": zone_c, "type": "Normal", "status": "Available", "x": 0.398, "y": 0.785, "w": 0.055, "h": 0.115, "price": 30.0, "notes": "South Lower Bay"},
    ]

    for item in spaces_seed:
        space = ParkingSpace(
            floor_id=ground_floor.id,
            zone_id=item["zone"].id,
            space_code=item["code"],
            name=item["name"],
            type=item["type"],
            status=item["status"],
            x=item["x"],
            y=item["y"],
            width=item["w"],
            height=item["h"],
            rotation=0.0,
            price=item["price"],
            notes=item["notes"]
        )
        db.add(space)

    db.commit()

    # 7. Add sample active reservation
    p010 = db.query(ParkingSpace).filter(ParkingSpace.space_code == "P010").first()
    if p010 and demo_user:
        now = datetime.now(timezone.utc)
        res = Reservation(
            user_id=demo_user.id,
            parking_space_id=p010.id,
            start_time=now - timedelta(minutes=30),
            end_time=now + timedelta(hours=2),
            status="Active"
        )
        db.add(res)

    # 8. Add initial system logs
    init_logs = [
        SystemLog(actor_id=admin_user.id, actor_name=admin_user.name, action="SYSTEM_INIT", entity_type="System", description="ParkVision AI Smart Parking Platform initialized."),
        SystemLog(actor_id=admin_user.id, actor_name=admin_user.name, action="CREATE_LOCATION", entity_type="ParkingLocation", entity_id=str(central_loc.id), description="Created 'ParkVision Central Parking' in Hyderabad."),
        SystemLog(actor_id=admin_user.id, actor_name=admin_user.name, action="UPLOAD_FLOOR_PLAN", entity_type="Floor", entity_id=str(ground_floor.id), description="Architectural blueprint uploaded for Level 0 (Ground Floor)."),
        SystemLog(actor_id=admin_user.id, actor_name=admin_user.name, action="BATCH_LAYOUT_SAVED", entity_type="Floor", entity_id=str(ground_floor.id), description="Placed 20 parking bays with normalized coordinates across Zones A, B, and C.")
    ]
    db.add_all(init_logs)

    # 9. Initial notifications
    db.add(Notification(
        user_id=admin_user.id,
        type="SYSTEM",
        message="Ground Floor blueprint configured with 20 parking bays."
    ))

    db.commit()
    print("Database seeding completed successfully!")
