def test_ai_status(client):
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "demo"
    assert data["status"] == "active"
    assert "DEMO MODE" in data["label"]

def test_ai_predictions(client):
    res = client.get("/api/ai/predictions")
    assert res.status_code == 200
    data = res.json()
    assert data["label"] == "DEMO AI PREDICTION"
    assert "predictions" in data
    assert len(data["predictions"]) == 5

def test_ai_insights(client):
    res = client.get("/api/ai/insights")
    assert res.status_code == 200
    data = res.json()
    assert "insights" in data
    assert len(data["insights"]) >= 3
