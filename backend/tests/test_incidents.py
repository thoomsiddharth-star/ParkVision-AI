def test_get_incidents(client):
    res = client.get("/api/incidents")
    assert res.status_code == 200
    incidents = res.json()
    assert len(incidents) >= 4
    for inc in incidents:
        assert "type" in inc
        assert "severity" in inc
        assert "status" in inc

def test_get_incident_by_id(client):
    res = client.get("/api/incidents/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert "description" in data

def test_review_incident(client):
    # Find an open incident
    res = client.get("/api/incidents")
    open_inc = next((i for i in res.json() if i["status"] == "OPEN"), None)
    if open_inc:
        inc_id = open_inc["id"]
        review_res = client.post(f"/api/incidents/{inc_id}/review")
        assert review_res.status_code == 200
        data = review_res.json()
        assert data["success"] is True
        assert data["new_status"] == "REVIEWED"

def test_resolve_incident(client):
    res = client.post("/api/incidents/1/resolve")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["new_status"] == "RESOLVED"
