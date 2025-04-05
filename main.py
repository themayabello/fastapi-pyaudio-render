from fastapi import FastAPI
import pyaudio

app = FastAPI()

@app.get("/")
def pyaudio_test():
    p = pyaudio.PyAudio()
    return {
        "status": "SUCCESS - PyAudio working!",
        "device_count": p.get_device_count()
    }
