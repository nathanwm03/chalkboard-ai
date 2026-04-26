# ChalkBoard AI

Convert any document into a short animated educational video — right in your browser.

---

## Quick start

### Windows
```bat
set ANTHROPIC_API_KEY=sk-ant-...
run.bat
```

### Mac / Linux
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
bash run.sh
```

Then open **http://localhost:5000**

---

## Manual setup

### 1 — Install Python dependencies
```bash
pip install -r requirements.txt
```

**Windows** — TTS works out of the box via SAPI5 (built-in). No extra install needed.

**Mac** — pyttsx3 needs pyobjc:
```bash
pip install pyobjc
```

**Linux** — pyttsx3 needs espeak:
```bash
sudo apt-get install espeak
```

### 2 — Set your Anthropic API key

**Windows (cmd)**
```
set ANTHROPIC_API_KEY=sk-ant-...
```
**Windows (PowerShell)**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```
**Mac / Linux**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3 — Run
```bash
python app.py
```

---

## How to use

1. Upload a PDF, DOCX, PPTX, or paste text into the sidebar
2. Type your topic focus (e.g. "health risks", "photosynthesis")
3. Pick **Whiteboard** or **Slides** style and a color theme
4. Click **✨ Generate Video** — takes 30–90 seconds
5. Watch in-browser, click card chips to jump, download MP4

---

## Features

- **Two video styles:** Whiteboard (animated chalk writing) and Slides (modern presentation)
- **Three themes:** Clean, Colorful, Dark
- **TTS narration** via pyttsx3 — offline, no extra API (SAPI5 on Windows, espeak on Linux, AVFoundation on Mac)
- **Supported input:** PDF, DOCX, PPTX, TXT, or pasted text
- **In-browser playback** with card-by-card navigation chips
- **MP4 download**

---

## File structure

```
chalkboard_ai/
├── app.py            Flask backend (4 routes)
├── extractor.py      PDF / DOCX / PPTX / TXT extraction
├── generator.py      Claude API → JSON cards
├── renderer.py       Pillow frame rendering (1280×720 @ 24fps)
├── narrator.py       pyttsx3 TTS → WAV files
├── composer.py       moviepy → MP4 (v1 + v2 compatible)
├── run.sh            Linux/Mac startup script
├── run.bat           Windows startup script
├── requirements.txt
└── templates/
    └── index.html    Self-contained UI (Google Fonts + inline CSS/JS)
```

---

## Notes

- Temp files go to `<system temp>/chalkboard_ai/` and are wiped on each new generation
- If TTS fails for any reason the video renders silently (no crash)
- Fonts auto-detected: Arial/Calibri on Windows, Helvetica on Mac, DejaVu/Liberation on Linux
