FROM python:3.11-slim

# PyAudio dependencies
RUN apt-get update && \
    apt-get install -y \
        portaudio19-dev \
        libasound2-dev \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to /app, /app created by Docker
WORKDIR /app
# Copy everything from the backend folder into /app
# Another service takes care of the frontend, don't want to unnecesarily copy it over
COPY backend/ .

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=10000
EXPOSE $PORT

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
