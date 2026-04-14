import os
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.crowd_data import get_venue_data

SYSTEM_PROMPT = """You are CrowdPulse AI, an intelligent assistant helping users navigate crowded stadiums.

You have access to:
- Crowd density levels
- Wait times
- Location data

Your goals:
1. Help users avoid crowds
2. Suggest faster routes
3. Recommend better alternatives

Always prioritize:
- Safety
- Speed
- Convenience

Keep responses short, clear, and practical.

Current Venue Context Data:
{context}

Provide your response in JSON format exactly like this:
{
    "message": "Your text response here",
    "coordinates": {"lat": 12.34, "lng": 56.78} // optional, include only if you recommend a specific zone, else null
}
"""

def chat_with_ai(user_message: str, stadium_id: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    venue_data = get_venue_data(stadium_id)
    
    # Format the context for the AI
    zones_info = []
    for z in venue_data['zones']:
        zones_info.append(f"Zone: {z['name']}, Density: {z['density']:.2f} (0=empty, 1=packed), Wait Time: {z['wait_time']} mins, Lat: {z['lat']}, Lng: {z['lng']}")
    context_str = "\n".join(zones_info)
    
    if not api_key:
        # Fallback Mock AI Response
        best_zone = min(venue_data['zones'], key=lambda x: x['wait_time'])
        return {
            "message": f"[Mock Mode] I see you're looking for help. The fastest route right now is towards {best_zone['name']} with only a {best_zone['wait_time']} min wait.",
            "coordinates": {"lat": best_zone['lat'], "lng": best_zone['lng']}
        }

    try:
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
        # Parse the JSON response
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Fallback on error
        return {
            "message": "Sorry, I'm having trouble connecting right now, but please check the map for live data updates.",
            "coordinates": None
        }
