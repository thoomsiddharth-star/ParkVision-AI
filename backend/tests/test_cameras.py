def test_get_cameras(client):
    response = client.get("/api/cameras")
    assert response.status_code == 200
    cameras = response.json()
    assert len(cameras) >= 4
    for cam in cameras:
        assert "name" in cam
        assert "camera_number" in cam
        assert "status" in cam

def test_get_camera_by_id(client):
    response = client.get("/api/cameras/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "status" in data

def test_get_camera_status(client):
    response = client.get("/api/cameras/1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["fps"] == 30
    assert data["latency_ms"] == 14
    assert "DEMO" in data["mode"] or "LIVE" in data["mode"]
