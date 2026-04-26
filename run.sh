#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

# espeak is only needed on Linux for pyttsx3; Windows uses SAPI5 built-in
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  echo "Installing espeak for Linux TTS..."
  sudo apt-get install espeak -y 2>/dev/null || true
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Enter your Anthropic API key:"
  read -s ANTHROPIC_API_KEY
  export ANTHROPIC_API_KEY
fi

echo "Starting ChalkBoard AI on http://localhost:5000 ..."
python app.py
