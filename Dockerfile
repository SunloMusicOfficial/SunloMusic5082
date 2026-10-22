FROM python:3.12-slim

# System dependencies install karo (FFmpeg for music, Node for yt-dlp, Image libs for Pillow)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    npm \
    git \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Working directory set karo
WORKDIR /app

# Requirements copy aur install karo
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Baaki code copy karo
COPY . .

# Web dashboard ke liye port expose karo
EXPOSE 8080

# Bot aur Web Server dono ko ek saath start karo
CMD ["sh", "-c", "gunicorn web_server:app --bind 0.0.0.0:8080 & python SunloMusic.py"]
