import random
import math
import os
import requests

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

def _get_fallback_simulated_data(stadium_id: str):
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
    
    # Add washroom zones
    zones.extend([
        {"id": "washroom_1", "name": "Washroom (Near North Gate)", "lat": stadium["lat"] + 0.0015, "lng": stadium["lng"], "density": random.uniform(0.1, 0.4), "wait_time": random.randint(1, 5)},
        {"id": "washroom_2", "name": "Washroom (Near South Gate)", "lat": stadium["lat"] - 0.0015, "lng": stadium["lng"], "density": random.uniform(0.5, 0.9), "wait_time": random.randint(5, 15)}
    ])

    heatmap_points = generate_random_heatmap_points(stadium["lat"], stadium["lng"], stadium["radius"], count=100)
    
    return {
        "stadium_info": stadium,
        "zones": zones,
        "heatmap": heatmap_points,
        "data_source_label": "Simulated Data",
        "confidence_score": "Low"
    }

def _generate_simulated_data(stadium_id: str):
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return _get_fallback_simulated_data(stadium_id)
        
    if stadium_id not in STADIUMS:
        stadium_id = "eden_gardens"
    stadium = STADIUMS[stadium_id]
    
    try:
        # 1. Places API: Get place_id and exact location
        query = f"{stadium['name']} stadium"
        places_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={api_key}"
        places_res = requests.get(places_url, timeout=5).json()
        
        if places_res.get("status") != "OK" or not places_res.get("results"):
            return _get_fallback_simulated_data(stadium_id)
            
        place_info = places_res["results"][0]
        place_id = place_info["place_id"]
        place_lat = place_info["geometry"]["location"]["lat"]
        place_lng = place_info["geometry"]["location"]["lng"]
        
        # 2. Distance Matrix API: Simulate origins & travel time vs baseline
        offset = stadium["radius"] * 5
        origins = [
            f"{place_lat + offset},{place_lng}",
            f"{place_lat - offset},{place_lng}",
            f"{place_lat},{place_lng + offset}",
            f"{place_lat},{place_lng - offset}"
        ]
        origins_str = "|".join(origins)
        dest_str = f"place_id:{place_id}"
        
        dm_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origins_str}&destinations={dest_str}&departure_time=now&key={api_key}"
        dm_res = requests.get(dm_url, timeout=5).json()
        
        if dm_res.get("status") != "OK":
            return _get_fallback_simulated_data(stadium_id)
            
        total_duration = 0
        total_duration_in_traffic = 0
        valid_rows = 0
        
        for row in dm_res.get("rows", []):
            for element in row.get("elements", []):
                if element.get("status") == "OK":
                    duration = element.get("duration", {}).get("value", 0)
                    duration_in_traffic = element.get("duration_in_traffic", {}).get("value", duration)
                    if duration > 0:
                        total_duration += duration
                        total_duration_in_traffic += duration_in_traffic
                        valid_rows += 1
                        
        if valid_rows == 0:
            return _get_fallback_simulated_data(stadium_id)
            
        # 3. Derive ratio and density score
        ratio = total_duration_in_traffic / total_duration if total_duration > 0 else 1.0
        
        if ratio > 1.5:
            base_density = 0.8
            count = 150
        elif ratio >= 1.2:
            base_density = 0.5
            count = 80
        else:
            base_density = 0.2
            count = 30
            
        # 4. Generate heatmap points using density
        heatmap_points = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            r = stadium["radius"] * math.sqrt(random.uniform(0, 1))
            point_lat = place_lat + r * math.cos(angle)
            point_lng = place_lng + r * math.sin(angle)
            weight = base_density + random.uniform(0, 0.2)
            if weight > 1.0:
                weight = 1.0
            heatmap_points.append({"lat": point_lat, "lng": point_lng, "weight": weight})
            
        # 5. Generate zones matching density
        zones = [
            {"id": "gate_1", "name": "North Gate", "lat": place_lat + 0.001, "lng": place_lng, "density": min(base_density + random.uniform(0, 0.2), 1.0), "wait_time": int(base_density * 30)},
            {"id": "gate_2", "name": "South Gate", "lat": place_lat - 0.001, "lng": place_lng, "density": max(base_density - random.uniform(0, 0.1), 0.1), "wait_time": int(base_density * 20)},
            {"id": "food_1", "name": "Food Court A", "lat": place_lat, "lng": place_lng + 0.001, "density": min(base_density + random.uniform(0, 0.2), 1.0), "wait_time": int(base_density * 25)},
            {"id": "exit_1", "name": "East Exit", "lat": place_lat, "lng": place_lng - 0.001, "density": max(base_density - random.uniform(0, 0.2), 0.1), "wait_time": int(base_density * 10)},
        ]
        
        zones.extend([
            {"id": "washroom_1", "name": "Washroom (Near North Gate)", "lat": place_lat + 0.0015, "lng": place_lng, "density": min(base_density + 0.1, 1.0), "wait_time": int(base_density * 15)},
            {"id": "washroom_2", "name": "Washroom (Near South Gate)", "lat": place_lat - 0.0015, "lng": place_lng, "density": max(base_density - 0.1, 0.1), "wait_time": int(base_density * 25)}
        ])
        
        stadium_info = dict(stadium)
        stadium_info["lat"] = place_lat
        stadium_info["lng"] = place_lng
        stadium_info["place_id"] = place_id
        
        confidence = "High" if ratio > 1.2 else "Medium"
        
        return {
            "stadium_info": stadium_info,
            "zones": zones,
            "heatmap": heatmap_points,
            "data_source_label": "Live Traffic Data",
            "confidence_score": confidence
        }
        
    except Exception as e:
        print(f"Error fetching real world traffic data: {e}")
        return _get_fallback_simulated_data(stadium_id)

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
