import os
import json
import math
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.crowd_data import get_crowd_data

SYSTEM_PROMPT = """You are CrowdPulse AI, an intelligent assistant helping users navigate crowded stadiums.

You have access to:
- Crowd density levels
- Wait times
- Location data
- User distance to zones (if available)

Your goals:
1. Help users avoid crowds.
2. Suggest faster routes and the nearest less-crowded options.
3. Recommend better alternatives naturally and conversationally. Avoid robotic phrasing like "I do not have data".

Important Intents:
- If asked about "washroom", "toilet", or "restroom", guide them to the nearest and least crowded Washroom zone.
- If asked about "food" or "eat", guide them to Food Court options.
- If the user asks vague navigation questions, guide them to the least crowded Gate or Exit.

Always prioritize Safety, Speed, and Convenience.
Data comes from live traffic updates or simulated sensors. A confidence score will be appended to your response by the system.

Current Venue Context Data:
{context}

Provide your response in JSON format exactly like this:
{
    "message": "Your text response here. Do not append confidence scores.",
    "coordinates": {"lat": 12.34, "lng": 56.78} // optional, include only if you recommend a specific zone, else null
}
"""

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def _get_best_zone_fallback(zones, user_message, user_lat=None, user_lng=None):
    msg_lower = user_message.lower()
    
    # 1. Intent Detection
    intent = None
    if any(keyword in msg_lower for keyword in ["washroom", "toilet", "restroom"]):
        intent = "washroom"
    elif any(keyword in msg_lower for keyword in ["food", "eat", "hungry", "snack"]):
        intent = "food"
    elif any(keyword in msg_lower for keyword in ["gate", "exit", "entry", "leave"]):
        intent = "gate"
        
    filtered_zones = []
    if intent == "washroom":
        filtered_zones = [z for z in zones if "washroom" in z['id']]
    elif intent == "food":
        filtered_zones = [z for z in zones if "food" in z['id']]
    elif intent == "gate":
        filtered_zones = [z for z in zones if "gate" in z['id'] or "exit" in z['id']]
        
    # 2. No clear intent -> default to gates/exits
    if not filtered_zones:
        intent = "gate"
        filtered_zones = [z for z in zones if "gate" in z['id'] or "exit" in z['id']]
        
    # 3. Find best option
    best_zone = None
    best_score = float('inf')
    
    for z in filtered_zones:
        # Score based on wait time primarily
        score = z['wait_time']
        
        # Add slight distance penalty if know user location (1 km = 10 mins walk penalty time)
        dist_str = ""
        if user_lat is not None and user_lng is not None:
            dist_km = haversine_distance(user_lat, user_lng, z['lat'], z['lng'])
            score += dist_km * 10 
            dist_str = f" (~{dist_km*1000:.0f}m away)"
            
        if score < best_score:
            best_score = score
            best_zone = (z, dist_str)
            
    return best_zone

def chat_with_ai(user_message: str, stadium_id: str, user_lat: float = None, user_lng: float = None):
    api_key = os.environ.get("GEMINI_API_KEY")
    venue_data = get_crowd_data(stadium_id, source="simulated")
    
    confidence = venue_data.get("confidence_score", "Low")
    conf_string = f"\n\n({confidence} confidence based on {venue_data.get('data_source_label', 'simulated data').lower()})"
    
    # Format the context for the AI
    zones_info = []
    for z in venue_data['zones']:
        dist_info = ""
        if user_lat is not None and user_lng is not None:
            dist_km = haversine_distance(user_lat, user_lng, z['lat'], z['lng'])
            dist_info = f", Distance: {dist_km*1000:.0f} meters"
        zones_info.append(f"Zone: {z['name']} (ID: {z['id']}), Density: {z['density']:.2f} (0=empty, 1=packed), Wait Time: {z['wait_time']} mins{dist_info}, Lat: {z['lat']}, Lng: {z['lng']}")
        
    context_str = "\n".join(zones_info)
    
    try:
        if not api_key:
            raise ValueError("No API Key")
            
        client = genai.Client(api_key=api_key)
        prompt_with_context = SYSTEM_PROMPT.replace("{context}", context_str)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=prompt_with_context,
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        data['message'] = data.get('message', '') + conf_string
        return data
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Smart Fallback
        best_zone_info = _get_best_zone_fallback(venue_data['zones'], user_message, user_lat, user_lng)
        
        if best_zone_info and best_zone_info[0]:
            z, dist_str = best_zone_info
            msg = f"Based on current congestion, {z['name']} is the fastest option (~{z['wait_time']} mins wait){dist_str}."
            return {
                "message": msg + conf_string,
                "coordinates": {"lat": z['lat'], "lng": z['lng']}
            }
        else:
            return {
                "message": "I'm having trouble routing right now, please check the live map for the least crowded areas." + conf_string,
                "coordinates": None
            }
