def test_recommendations_endpoint(client):
    res = client.get("/api/recommendations?latitude=12.9716&longitude=77.5946&sort_by=balanced")
    assert res.status_code == 200
    data = res.json()
    assert data["total_found"] >= 4
    recs = data["recommendations"]
    assert len(recs) >= 4
    for r in recs:
        assert "score" in r
        assert "score_breakdown" in r
        assert 0.0 <= r["score"] <= 100.0

def test_recommendations_sort_keys(client):
    for sort_key in ["distance", "availability", "price", "ev", "balanced"]:
        res = client.get(f"/api/recommendations?latitude=12.9716&longitude=77.5946&sort_by={sort_key}")
        assert res.status_code == 200
        data = res.json()
        assert data["sort_by"] == sort_key
