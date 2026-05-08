def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") in ("ok", "healthy")


def test_root_returns_metadata(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body or "name" in body
