@echo off
echo Installing dependencies...
pip install -r requirements.txt

if "%ANTHROPIC_API_KEY%"=="" (
    set /p ANTHROPIC_API_KEY="Enter your Anthropic API key: "
)

echo Starting ChalkBoard AI on http://localhost:5000 ...
python app.py
