FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    npm \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8080
CMD ["sh", "-c", "gunicorn web_server:app --bind 0.0.0.0:8080 & python SunloMusic.py"]
