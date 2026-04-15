from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.config import settings

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    assert "google_maps_enabled" in response.json()

def test_crowd_data_valid():
    response = client.get("/api/stadium/eden_gardens/crowd-data")
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data["data"]
    assert "heatmap" in data["data"]

def test_crowd_data_invalid_stadium():
    # Should fallback securely
    response = client.get("/api/stadium/invalid_stadium_123/crowd-data")
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data["data"]
    # Fallback usually goes to eden_gardens, check lat/lng approx
    assert data["data"]["stadium_info"]["name"] == "Eden Gardens"

def test_crowd_data_api_failure(mocker):
    # Mock requests.get to simulate API failure
    mocker.patch('requests.get', side_effect=Exception("Simulated Network Error"))
    response = client.get("/api/stadium/narendra_modi/crowd-data?source=stadium_api")
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data["data"]
    assert data["data"]["data_source_label"] == "Simulated Data"

def test_crowd_data_with_mocked_google_maps(mocker):
    original_api_key = settings.google_maps_api_key
    settings.google_maps_api_key = "dummy_key"
    try:
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
            def json(self):
                return self.json_data
            def raise_for_status(self):
                pass
                
        def mock_requests_get(url, *args, **kwargs):
            if "place/textsearch" in url:
                return MockResponse({"status": "OK", "results": [{"place_id": "test_id", "geometry": {"location": {"lat": 10.0, "lng": 20.0}}}]}, 200)
            if "distancematrix" in url:
                return MockResponse({"status": "OK", "rows": [{"elements": [{"status": "OK", "duration": {"value": 10}, "duration_in_traffic": {"value": 15}}]}]}, 200)
            return MockResponse({}, 200)
            
        mocker.patch('requests.get', side_effect=mock_requests_get)
        # Call it once to populate the cache or hit the cache
        response = client.get("/api/stadium/cache_buster_1/crowd-data")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["data_source_label"] == "Live Traffic Data"
        assert data["data"]["confidence_score"] == "Medium" or data["data"]["confidence_score"] == "High"
    finally:
        settings.google_maps_api_key = original_api_key

def test_crowd_data_with_mocked_google_maps_high_traffic(mocker):
    original_api_key = settings.google_maps_api_key
    settings.google_maps_api_key = "dummy_key"
    try:
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
            def json(self):
                return self.json_data
            def raise_for_status(self):
                pass
                
        def mock_requests_get(url, *args, **kwargs):
            if "place/textsearch" in url:
                return MockResponse({"status": "OK", "results": [{"place_id": "test_id2", "geometry": {"location": {"lat": 10.0, "lng": 20.0}}}]}, 200)
            if "distancematrix" in url:
                return MockResponse({"status": "OK", "rows": [{"elements": [{"status": "OK", "duration": {"value": 10}, "duration_in_traffic": {"value": 20}}]}]}, 200)
            return MockResponse({}, 200)
            
        mocker.patch('requests.get', side_effect=mock_requests_get)
        response = client.get("/api/stadium/cache_buster_2/crowd-data")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["confidence_score"] == "High"
    finally:
        settings.google_maps_api_key = original_api_key

def test_chat_valid(mocker):
    class MockClient:
        def __init__(self, api_key):
            self.models = MockModels()
    class MockModels:
        def generate_content(self, model, contents, config):
            class MockResponse:
                text = '{"message": "Turn left for food."}'
            return MockResponse()
            
    mocker.patch('google.genai.Client', MockClient)
    original_key = settings.gemini_api_key
    settings.gemini_api_key = "dummy"
    try:
        response = client.post('/api/chat', json={
            "message": "Which gate is least crowded?",
            "stadium_id": "eden_gardens",
            "user_lat": 22.0,
            "user_lng": 88.0
        })
        assert response.status_code == 200
        assert "Turn left for food" in response.json()["message"]
    finally:
        settings.gemini_api_key = original_key

def test_chat_invalid_missing_fields():
    response = client.post('/api/chat', json={
        "message": "Hi"
    })
    assert response.status_code == 422 # Unprocessable Entity (missing stadium_id)

def test_chat_invalid_empty_stadium():
    response = client.post('/api/chat', json={
        "message": "Hi",
        "stadium_id": ""
    })
    assert response.status_code == 422 # Failed validation min_length

def test_chat_ai_fallback(mocker):
    # Simulating Gemini failure
    mocker.patch('google.genai.Client', side_effect=Exception("Missing Key or Quota"))
    response = client.post('/api/chat', json={
        "message": "food",
        "stadium_id": "eden_gardens"
    })
    assert response.status_code == 200
    data = response.json()
    assert "fastest option" in data["message"] or "trouble routing" in data["message"]

def test_chat_ai_fallback_no_stadium(mocker):
    mocker.patch('google.genai.Client', side_effect=Exception("Missing Key or Quota"))
    # The API should gracefully fallback even if stadium id is invalid, it falls back to eden_gardens
    response = client.post('/api/chat', json={
        "message": "find washroom",
        "stadium_id": "invalid_stadium_id",
        "user_lat": 22.0,
        "user_lng": 88.0
    })
    assert response.status_code == 200
    data = response.json()
    assert "fastest option" in data["message"]

def test_source_placeholders():
    sources = ["stadium_api", "iot_sensors", "camera_vision"]
    for src in sources:
        res = client.get(f"/api/stadium/eden_gardens/crowd-data?source={src}")
        assert res.status_code == 200
        assert "zones" in res.json()["data"]

def test_chat_endpoint_internal_error(mocker):
    mocker.patch('app.main.chat_with_ai', side_effect=Exception("Database Timeout"))
    response = client.post('/api/chat', json={
        "message": "Hi",
        "stadium_id": "eden_gardens"
    })
    assert response.status_code == 200
    data = response.json()
    assert "trouble" in data["message"]
    assert data["coordinates"] is None
