#!/bin/bash
# SunloMusic Auto Installer for Termux (Ubuntu Proot)
# Usage: bash scripts/install_termux_ubuntu.sh

echo "🚀 Starting SunloMusic Installation..."

# Update system
echo "📦 Updating packages..."
apt update && apt upgrade -y

# Install required dependencies (Python 3.12 setup)
echo "🛠️ Installing dependencies..."
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.12 python3.12-venv python3.12-dev ffmpeg git build-essential libssl-dev

# Setup Virtual Environment
echo "🐍 Setting up Virtual Environment..."
python3.12 -m venv venv
source venv/bin/activate

# Install Requirements
echo "📥 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Installation Complete!"
echo "Ab aap 'source venv/bin/activate' chala kar 'python SunloMusic.py' se bot start kar sakte hain."
