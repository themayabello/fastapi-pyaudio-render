from fastapi import FastAPI
import pyaudio
from scene_runner import get_user_character_and_script

app = FastAPI()


# Required endpoint for Render's health checks
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def pyaudio_test():
    p = pyaudio.PyAudio()
    return {
        "status": "SUCCESS - PyAudio working!",
        "device_count": p.get_device_count()
    }

@app.get("/test-scene-runner")
def test_scene_runner():
    try:
        script, char = get_user_character_and_script()  # This will trigger imports
        return {"status": "SUCCESS", "character": char}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}  # Reveals missing deps
