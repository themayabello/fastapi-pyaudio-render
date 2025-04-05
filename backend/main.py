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
