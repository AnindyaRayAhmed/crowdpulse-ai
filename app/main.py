import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from app.ai_engine import chat_with_ai
from app.crowd_data import get_crowd_data

# Load environment variables
load_dotenv()

app = FastAPI(title="CrowdPulse AI API")

# Setup static files and templates
# For nested routing inside the app directory
base_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

class ChatRequest(BaseModel):
    message: str
    stadium_id: str

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/config")
async def get_config():
    """Returns necessary frontend configurations like the maps API key."""
    return JSONResponse({
        "google_maps_api_key": os.environ.get("GOOGLE_MAPS_API_KEY", "")
    })

@app.get("/api/stadium/{stadium_id}/crowd-data")
async def get_crowd_data_endpoint(stadium_id: str, source: str = "simulated"):
    """Returns crowd data for a given stadium based on the data source."""
    data = get_crowd_data(stadium_id, source=source)
    return JSONResponse({"data": data})

@app.post("/api/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """Handles the AI chat."""
    response_data = chat_with_ai(chat_request.message, chat_request.stadium_id)
    return JSONResponse(response_data)
