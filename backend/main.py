from fastapi import FastAPI
import pyaudio

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

# Temporarily add to main.py
try:
    from scene_runner import get_user_character_and_script  # Replace with a real function
    print("scene_runner imports successfully!")
except Exception as e:
    print(f"scene_runner import FAILED: {str(e)}")
