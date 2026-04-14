import random
import math
import os

# Placeholder configuration for secure access (future integration)
# E.g., read from environment variables:
STADIUM_API_KEY = os.environ.get("STADIUM_API_KEY", "")
IOT_AUTH_TOKEN = os.environ.get("IOT_AUTH_TOKEN", "")

# Predefined dataset of major stadiums
STADIUMS = {
    "eden_gardens": {
        "name": "Eden Gardens",
        "lat": 22.564551128342874,
        "lng": 88.34331627118985,
        "radius": 0.002 # approximate radius in degrees for points spread
    },
    "wankhede": {
        "name": "Wankhede Stadium",
        "lat": 18.938888,
        "lng": 72.825833,
        "radius": 0.0015
    },
    "narendra_modi": {
        "name": "Narendra Modi Stadium",
        "lat": 23.091763,
        "lng": 72.597519,
        "radius": 0.0025
    }
}

def generate_random_heatmap_points(lat, lng, radius, count=50):
    points = []
    for _ in range(count):
        # Generate random angle and distance within radius
        angle = random.uniform(0, 2 * math.pi)
        r = radius * math.sqrt(random.uniform(0, 1))
        
        point_lat = lat + r * math.cos(angle)
        point_lng = lng + r * math.sin(angle)
        
        # Density weight
        weight = random.uniform(0.1, 1.0)
        
        points.append({
            "lat": point_lat,
            "lng": point_lng,
            "weight": weight
        })
    return points

def fetch_stadium_api_data(stadium_id: str):
    """
    Placeholder: Fetch live data from official Stadium APIs using STADIUM_API_KEY.
    Returns mock data for now.
    """
    # TODO: Implement real API request here
    # Example: response = requests.get(f"https://api.stadium.example/status?id={stadium_id}", headers={"Authorization": f"Bearer {STADIUM_API_KEY}"})
    return _generate_simulated_data(stadium_id)

def fetch_iot_sensor_data(stadium_id: str):
    """
    Placeholder: Fetch live data from IoT sensors deployed at turnstiles and gates using IOT_AUTH_TOKEN.
    Returns mock data for now.
    """
    # TODO: Implement real MQTT/HTTP call to IoT data broker
    return _generate_simulated_data(stadium_id)

def fetch_camera_data(stadium_id: str):
    """
    Placeholder: Fetch crowd density estimates from camera-based computer vision analytics.
    Returns mock data for now.
    """
    # TODO: Implement connection to video analytics engine
    return _generate_simulated_data(stadium_id)

def _generate_simulated_data(stadium_id: str):
    if stadium_id not in STADIUMS:
        stadium_id = "eden_gardens" # Fallback
        
    stadium = STADIUMS[stadium_id]
    
    # Generate zones simulating gates, food, exits
    zones = [
        {"id": "gate_1", "name": "North Gate", "lat": stadium["lat"] + 0.001, "lng": stadium["lng"], "density": random.uniform(0.5, 1.0), "wait_time": random.randint(5, 30)},
        {"id": "gate_2", "name": "South Gate", "lat": stadium["lat"] - 0.001, "lng": stadium["lng"], "density": random.uniform(0.1, 0.6), "wait_time": random.randint(1, 15)},
        {"id": "food_1", "name": "Food Court A", "lat": stadium["lat"], "lng": stadium["lng"] + 0.001, "density": random.uniform(0.6, 1.0), "wait_time": random.randint(10, 25)},
        {"id": "exit_1", "name": "East Exit", "lat": stadium["lat"], "lng": stadium["lng"] - 0.001, "density": random.uniform(0.2, 0.5), "wait_time": random.randint(1, 5)},
    ]
    
    heatmap_points = generate_random_heatmap_points(stadium["lat"], stadium["lng"], stadium["radius"], count=100)
    
    return {
        "stadium_info": stadium,
        "zones": zones,
        "heatmap": heatmap_points
    }

def get_crowd_data(stadium_id: str, source: str = "simulated"):
    """
    Unified function for returning stadium crowd data based on the selected source.
    """
    if source == "stadium_api":
        return fetch_stadium_api_data(stadium_id)
    elif source == "iot_sensors":
        return fetch_iot_sensor_data(stadium_id)
    elif source == "camera_vision":
        return fetch_camera_data(stadium_id)
    else:
        # Default behavior: simulated demo mode
        return _generate_simulated_data(stadium_id)
