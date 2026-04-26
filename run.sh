#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing espeak for voice narration..."
sudo apt-get install espeak -y 2>/dev/null || true

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Enter your Anthropic API key:"
  read -s ANTHROPIC_API_KEY
  export ANTHROPIC_API_KEY
fi

echo "Starting ChalkBoard AI on http://localhost:5000 ..."
python app.py
