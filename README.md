# ChalkBoard AI

Convert any document into a short animated educational video — right in your browser.

---

## Quick start

### Windows
```bat
set ANTHROPIC_API_KEY=sk-ant-...
set GOOGLE_TTS_KEY=AIza...
run.bat
```

### Mac / Linux
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_TTS_KEY="AIza..."
bash run.sh
```

Then open **http://localhost:5000**

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude API key — generates the video script |
| `GOOGLE_TTS_KEY` | Yes | Google Cloud TTS API key — generates voiceover audio |

If `GOOGLE_TTS_KEY` is missing the video will still render, just without audio.

**Getting a Google TTS API key:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the **Cloud Text-to-Speech API**
3. Create an API key under **APIs & Services → Credentials**

---

## Manual setup

### 1 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2 — Set environment variables

**Windows (cmd)**
```
set ANTHROPIC_API_KEY=sk-ant-...
set GOOGLE_TTS_KEY=AIza...
```
**Windows (PowerShell)**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:GOOGLE_TTS_KEY="AIza..."
```
**Mac / Linux**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_TTS_KEY="AIza..."
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
- **TTS narration** via Google Cloud Text-to-Speech Neural2 voice (en-US-Neural2-D)
- **Supported input:** PDF, DOCX, PPTX, TXT, or pasted text
- **In-browser playback** with card-by-card navigation chips
- **MP4 download**

---

## File structure

```
├── app.py            Flask backend (4 routes)
├── extractor.py      PDF / DOCX / PPTX / TXT extraction
├── generator.py      Claude API → JSON cards
├── renderer.py       Pillow frame rendering (1280×720 @ 24fps)
├── narrator.py       Google TTS REST API → MP3 files
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
