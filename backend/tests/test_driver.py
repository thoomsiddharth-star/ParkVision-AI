def test_driver_search(client):
    payload = {
        "destination": "Commercial Hub",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "preferences": {
            "max_distance_km": 15.0,
            "max_price_per_hour": 70.0,
            "ev_required": False,
            "accessible_required": False
        }
    }
    res = client.post("/api/driver/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "recommended_lots" in data
    assert data["matches_count"] >= 1

def test_driver_search_ev_filter(client):
    payload = {
        "destination": "Commercial Hub",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "preferences": {
            "max_distance_km": 20.0,
            "ev_required": True
        }
    }
    res = client.post("/api/driver/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    for lot in data["recommended_lots"]:
        assert lot["ev_available"] > 0
