def test_analytics_occupancy(client):
    for period in ["today", "7d", "30d"]:
        res = client.get(f"/api/analytics/occupancy?period={period}")
        assert res.status_code == 200
        data = res.json()
        assert data["period"] == period
        assert len(data["data"]) > 0
        assert "occupancy" in data["data"][0]

def test_analytics_demand(client):
    res = client.get("/api/analytics/demand?period=today")
    assert res.status_code == 200
    data = res.json()
    assert "data" in data
    assert len(data["data"]) > 0

def test_analytics_peak_hours(client):
    res = client.get("/api/analytics/peak-hours?period=today")
    assert res.status_code == 200
    data = res.json()
    assert "busiest_time" in data
    assert len(data["data"]) > 0

def test_analytics_duration(client):
    res = client.get("/api/analytics/parking-duration?period=today")
    assert res.status_code == 200
    data = res.json()
    assert "average_duration" in data
    assert len(data["data"]) > 0

def test_analytics_ev_utilization(client):
    res = client.get("/api/analytics/ev-utilization?period=today")
    assert res.status_code == 200
    data = res.json()
    assert "overall_ev_utilization" in data
    assert len(data["data"]) > 0
