<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=35&pause=1000&color=36BCF7&center=true&vCenter=true&width=800&lines=Welcome+to+Sunlo+Music;Fastest+%26+Most+Advanced+Bot;200%2B+Features+%7C+1-3s+Playback;Premium+Telegram+Music+Experience" alt="Typing SVG" />

<br>

**The Ultimate, Lightning-Fast Telegram Voice Chat Music Bot.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FTMGram](https://img.shields.io/badge/Framework-FTMGram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://github.com)
[![PyTgCalls](https://img.shields.io/badge/Engine-PyTgCalls_v2.x-FF5722?style=for-the-badge&logo=webrtc&logoColor=white)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen?style=for-the-badge)](https://github.com/SunloMusicOfficial)
[![Profile Views](https://komarev.com/ghpvc/?username=SunloMusicOfficial&color=blueviolet&style=for-the-badge)](https://github.com/SunloMusicOfficial)

---

</div>

## ⚡ Why Sunlo Music?

Tired of slow bots that take 5-10 seconds to play a song? **Sunlo Music** is built from scratch with a focus on **extreme speed, stability, and a premium user experience**. 

- 🚀 **Ultra-Fast Streaming:** 1-3 second playback using direct URL extraction and smart preloading.
- 🪶 **Lightweight Core:** Highly optimized memory management. Runs flawlessly on low-end VPS.
- 🎛 **200+ Premium Features:** Equalizers, AI recommendations, playlists, live lyrics, and much more.
- 🛡 **Zero Leakage:** Built on FTMGram to ensure no file descriptor leaks, guaranteeing 99.9% uptime.

---

## 📋 Prerequisites (Zaroori Cheezein)
Bot deploy karne se pehle aapke paas yeh hona chahiye:
1. **Telegram API ID & HASH** (from [my.telegram.org](https://my.telegram.org))
2. **Bot Token** (from [@BotFather](https://t.me/BotFather))
3. **MongoDB URI** (from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Free tier)
4. **Pyrogram Session String** (Assistant account ke liye - script included hai)

---

## 🚀 Deployment Guides & Commands

### 1️⃣ Termux (Local Testing)
**Guide:** 
Termux ka default Python abhi unstable hota hai, isliye hum ek Ubuntu environment banayenge `proot-distro` ke through. Isme Python 3.12 aur zaroori libraries install karenge, phir bot clone karke run karenge.

**Commands:**
```bash
# 1. Termux mein Ubuntu setup karein
pkg update && pkg upgrade -y
pkg install proot-distro -y
proot-distro install ubuntu
proot-distro login ubuntu

# 2. Ubuntu ke andar dependencies install karein
apt update && apt upgrade -y
apt install -y python3.12 python3.12-venv python3.12-dev ffmpeg git build-essential

# 3. Bot ko clone karein aur environment setup karein
git clone https://github.com/SunloMusicOfficial/SunloMusic.git
cd SunloMusic
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Environment variables set karein
cp .env.example .env
nano .env # Apni details daalein (Ctrl+O, Enter, Ctrl+X se save karein)

# 5. Session Generate karein (Assistant Account)
python scripts/generate_session.py

# 6. Bot Start karein
python SunloMusic.py
```

---

### 2️⃣ VPS (Ubuntu / Debian)
**Guide:** 
Agar aapke paas VPS hai (DigitalOcean, AWS, etc.), toh aapko Python 3.12 ki zaroorat padegi. Ubuntu 22.04 par yeh default nahi hota, isliye hum `deadsnakes` PPA ka use karke ise install karenge. Phir virtual environment banakar bot ko 24/7 run kar sakte hain.

**Commands:**
```bash
# 1. System update aur Python 3.12 install karein
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev ffmpeg git build-essential

# 2. Clone and Setup
git clone https://github.com/SunloMusicOfficial/SunloMusic.git
cd SunloMusic
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure and Run
cp .env.example .env
nano .env # Details fill karein
python scripts/generate_session.py
python SunloMusic.py
```
*(Tip: VPS par bot ko 24/7 chalane ke liye `tmux` ya `screen` ka use karein).*

---

### 3️⃣ Docker (For Advanced Users)
**Guide:** 
Agar aap Docker use karte hain, toh aapko manually Python install karne ki zaroorat nahi hai. Bas ek `.env` file banayein, image build karein, aur container run kar dein.

**Commands:**
```bash
# 1. Clone Repository
git clone https://github.com/SunloMusicOfficial/SunloMusic.git
cd SunloMusic

# 2. Setup .env
cp .env.example .env
nano .env

# 3. Build & Run Container
docker build -t sunlo-music .
docker run -d --name sunlo-bot --env-file .env --restart unless-stopped sunlo-music
```

---

### 4️⃣ Cloud Platforms (Heroku / Railway / Render)
**Guide:** 
In platforms par aapko sirf GitHub repo link karni hai aur dashboard mein Environment Variables add karne hain. Koi terminal command nahi chalani padti.

1. Apna GitHub repo fork/clone karein.
2. Railway/Heroku par naya project banayein aur GitHub connect karein.
3. **Settings > Environment Variables** mein jayein aur `.env.example` mein diye gaye saare variables (API_ID, API_HASH, BOT_TOKEN, MONGO_URI, etc.) add karein.
4. **Start Command** set karein: `python SunloMusic.py`
5. **Note:** Heroku/Render ke ephemeral disk par cache save nahi hota, isliye playback ke liye MongoDB aur proper caching logic zaroori hai.

---

## 🎯 Features Breakdown

<table>
  <tr>
    <td width="50%">
      <h3>🎵 Core Streaming</h3>
      <ul>
        <li>Multi-Platform (YouTube, Spotify, SoundCloud)</li>
        <li>Gapless Playback & Crossfade</li>
        <li>Smart Queue & Preloading</li>
        <li>Live Synced Lyrics</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🎛 Audio Effects</h3>
      <ul>
        <li>Real-time Equalizer</li>
        <li>Bass Boost & Nightcore</li>
        <li>8D Audio & Slowed+Reverb</li>
        <li>Variable Playback Speed</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>👤 User Engagement</h3>
      <ul>
        <li>Personal Saved Playlists</li>
        <li>Song Requests & Voting</li>
        <li>Listening History & Stats</li>
        <li>AI DJ (Mood-based songs)</li>
      </ul>
    </td>
    <td width="50%">
      <h3>🛡 Admin & Moderation</h3>
      <ul>
        <li>Role-Based Access (Sudo/Admin)</li>
        <li>Anti-Spam & Rate Limiting</li>
        <li>Broadcast System</li>
        <li>Auto-Leave Inactive VCs</li>
      </ul>
    </td>
  </tr>
</table>

---

## 📁 Project Architecture

```text
SunloMusic/
├── SunloMusic.py         # Main Entry Point
├── config/               # Settings & Constants
├── core/                 # Bot, Userbot, DB & Calls Engine
├── plugins/              # Commands (Play, Controls, Admin)
├── utils/                # Fast Downloader, Cache & Logger
├── database/             # MongoDB CRUD Operations
├── scripts/              # Session Generator & Installers
├── assets/               # Images & Language Files
└── cache/                # Downloaded Songs Cache
```

---

## 👑 Credits & Support

<div align="center">

**Developed with ❤️ by Sakil**

[![Telegram Support](https://img.shields.io/badge/Join-Support%20Chat-blue?style=for-the-badge&logo=telegram)](https://t.me/YO_UR_OFFICIAL_CRUSH)
[![Telegram Channel](https://img.shields.io/badge/Join-Update%20Channel-blue?style=for-the-badge&logo=telegram)](https://t.me/Vip_Sakil_Bio)

<br>

**Bot Live At:** [@SunloMusicBot](https://t.me/SunloMusicBot)

</div>

---
<div align="center">
  <b>⭐ If you like this project, don't forget to Star the repository! ⭐</b>
</div>
