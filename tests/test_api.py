from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_crowd_data():
    response = client.get("/api/stadium/eden_gardens/crowd-data")
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data
    assert "heatmap" in data

def test_chat():
    response = client.post("/api/chat", json={
        "message": "Which gate is least crowded?"
    })
    assert response.status_code == 200
