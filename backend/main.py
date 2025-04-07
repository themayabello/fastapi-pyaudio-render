from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
import tempfile
import requests
import json

from scene_runner import parse_script_from_pdf, extract_characters

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "cjVigY5qzO86Huf0OWal")

app = FastAPI()

# CORS middleware - must be under "app=FastAPI()"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.mbcreativeenterprises.com", "https://mbcreativeenterprises.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files - must be under "app=FastAPI()"
app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# Global script storage (in production use a database)
SCRIPT_STORAGE = {}


# --- Core Functions ---
def generate_audio(text, output_path):
    """Generate audio using ElevenLabs"""
    print(f"🎤 Generating audio: {output_path}")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
    else:
        raise Exception(f"ElevenLabs error: {response.text}")


# @app.get("/")
# async def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# --- API Endpoints ---
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Offer Only API",
        "status": "ok",
        "port": os.getenv("PORT", 10000)
    }


# Required endpoint for Render's health checks
@app.get("/health")
def health_check():
    return {"status": "ok"}


# for debugging -  logs all your registered routes
@app.on_event("startup")
async def print_routes():
    print("Registered routes:")
    for route in app.routes:
        print(f"- {route.path} ({route.methods})")


@app.post("/upload_script")
async def upload_script(file: UploadFile = File(...)):
    """Process uploaded script PDF"""
    contents = await file.read()
    temp_path = "temp_script.pdf"
    with open(temp_path, "wb") as f:
        f.write(contents)

    lines = parse_script_from_pdf(temp_path)
    characters = extract_characters(lines)
    script_id = os.urandom(8).hex()

    SCRIPT_STORAGE[script_id] = {
        "characters": characters,
        "lines": lines
    }
    return {"script_id": script_id, "characters": characters}


@app.post("/start_scene")
async def start_scene(script_id: str = Form(...),
                      character: str = Form(...)):
    """Initialize a scene with selected character"""
    if script_id not in SCRIPT_STORAGE:
        return {"error": "Script not found"}

    return {
        "message": f"Scene started as {character}",
        "script_id": script_id,
        "current_position": 0
    }


@app.post("/get_next_line")
async def get_next_line(script_id: str = Form(...),
                        current_position: int = Form(0),
                        character: str = Form(...)):
    """Get the next line in the scene"""
    if script_id not in SCRIPT_STORAGE:
        return {"error": "Script not found"}

    script = SCRIPT_STORAGE[script_id]
    if current_position >= len(script["lines"]):
        return {"action": "scene_complete"}

    line = script["lines"][current_position]

    # Skip scene directions and empty lines
    if (not line.strip() or
            line.startswith(('INT.', 'EXT.', 'FADE', 'CUT TO', 'DISSOLVE')) or
            (line.startswith('(') and line.endswith(')'))):
        return {
            "action": "continue",
            "next_position": current_position + 1
        }

    # Character name detection (all caps, not a scene direction)
    if line.isupper() and 1 <= len(line.split()) <= 3:
        current_char = line
        next_position = current_position + 1
        # Get the dialogue text (skip parenthetical if present)
        while (next_position < len(script["lines"]) and
               (not script["lines"][next_position].strip() or
                (script["lines"][next_position].startswith('(') and
                 script["lines"][next_position].endswith(')')))):
            next_position += 1

        if next_position >= len(script["lines"]):
            return {"action": "scene_complete"}

        line_text = script["lines"][next_position]

        if current_char == character.upper():
            return {
                "action": "user_turn",
                "prompt": line_text,
                "next_position": next_position + 1
            }
        else:
            # Generate AI response
            output_path = f"static/response_{script_id}_{current_position}.mp3"
            generate_audio(line_text, output_path)

            return {
                "action": "play_audio",
                "audio_url": f"/static/response_{script_id}_{current_position}.mp3",
                "next_text": f"{current_char}: {line_text}",
                "next_position": next_position + 1
            }

    return {
        "action": "continue",
        "next_position": current_position + 1
    }
