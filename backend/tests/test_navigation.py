def test_navigation_endpoint(client):
    params = {
        "origin_latitude": 12.9650,
        "origin_longitude": 77.5850,
        "destination_latitude": 12.9716,
        "destination_longitude": 77.5946,
        "destination_name": "Central Mall Parking"
    }
    res = client.get("/api/navigation", params=params)
    assert res.status_code == 200
    data = res.json()
    assert "distance" in data
    assert "estimated_time" in data
    assert len(data["polyline"]) > 0
    assert len(data["steps"]) > 0
    assert data["destination_name"] == "Central Mall Parking"
