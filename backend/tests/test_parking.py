def test_get_parking_lots(client):
    response = client.get("/api/parking/lots")
    assert response.status_code == 200
    lots = response.json()
    assert len(lots) >= 4
    names = [l["name"] for l in lots]
    assert "Central Mall Parking" in names
    assert "City Center Parking" in names

def test_get_parking_lot_by_id(client):
    response = client.get("/api/parking/lots/1")
    assert response.status_code == 200
    lot = response.json()
    assert lot["id"] == 1
    assert lot["capacity"] == 40
    assert lot["price_per_hour"] > 0

def test_get_lot_not_found(client):
    response = client.get("/api/parking/lots/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "LOT_NOT_FOUND"

def test_get_lot_spaces(client):
    response = client.get("/api/parking/lots/1/spaces")
    assert response.status_code == 200
    spaces = response.json()
    assert len(spaces) == 40
    # Central Mall has A01 to A40
    numbers = [s["space_number"] for s in spaces]
    assert "A01" in numbers
    assert "A40" in numbers

def test_get_space_by_id(client):
    response = client.get("/api/parking/spaces/1")
    assert response.status_code == 200
    space = response.json()
    assert space["id"] == 1
    assert "status" in space

def test_select_space_success(client):
    # Find an available space in lot 1
    spaces_resp = client.get("/api/parking/lots/1/spaces")
    avail_space = next(s for s in spaces_resp.json() if s["status"] == "AVAILABLE")
    space_id = avail_space["id"]

    response = client.post(f"/api/parking/spaces/{space_id}/select", json={"permanent_reservation": False})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["space_id"] == space_id
    assert "selected successfully" in data["message"]

def test_select_space_occupied_error(client):
    # Find an occupied space in lot 1
    spaces_resp = client.get("/api/parking/lots/1/spaces")
    occ_space = next(s for s in spaces_resp.json() if s["status"] == "OCCUPIED")
    space_id = occ_space["id"]

    response = client.post(f"/api/parking/spaces/{space_id}/select", json={"permanent_reservation": False})
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "SPACE_OCCUPIED"
    assert "currently occupied" in data["error"]["message"]

def test_get_live_parking(client):
    response = client.get("/api/parking/live?lot_id=1")
    assert response.status_code == 200
    live = response.json()
    assert live["total_spaces"] == 40
    assert live["available_spaces"] > 0
    assert live["occupied_spaces"] > 0
    assert 0.0 <= live["occupancy_percentage"] <= 100.0
    assert len(live["spaces"]) == 40

def test_legacy_aliases(client):
    res1 = client.get("/api/spaces")
    assert res1.status_code == 200
    assert "spaces" in res1.json()

    res2 = client.get("/api/locations")
    assert res2.status_code == 200
    assert "locations" in res2.json()

    res3 = client.get("/api/status")
    assert res3.status_code == 200
    assert "occupancyRate" in res3.json()
