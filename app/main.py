import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from app.config import settings
from app.ai_engine import chat_with_ai
from app.crowd_data import get_crowd_data
app = FastAPI(title="CrowdPulse AI API")

# Setup static files and templates
# For nested routing inside the app directory
base_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's chat message")
    stadium_id: str = Field(..., min_length=1, description="The stadium identifier")
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"google_maps_api_key": settings.google_maps_api_key}
    )

@app.get("/api/config")
async def get_config():
    """Returns frontend feature flags. API keys are never exposed here."""
    return JSONResponse({
        "google_maps_enabled": bool(settings.google_maps_api_key)
    })

@app.get("/api/stadium/{stadium_id}/crowd-data")
async def get_crowd_data_endpoint(stadium_id: str, source: str = "simulated"):
    """Returns crowd data for a given stadium based on the data source."""
    data = get_crowd_data(stadium_id, source=source)
    return JSONResponse({"data": data})

@app.post("/api/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """Handles the AI chat."""
    try:
        response_data = chat_with_ai(
            chat_request.message, 
            chat_request.stadium_id,
            chat_request.user_lat,
            chat_request.user_lng
        )
        return JSONResponse(response_data)
    except Exception:
        return JSONResponse({
            "message": "I'm having trouble right now, but I can still guide you. Try asking about gates or exits.",
            "coordinates": None
        })
