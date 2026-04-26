# ChalkBoard AI

Convert any document into a short animated educational video — right in your browser.

---

## Setup (3 steps)

### Step 1 — Install dependencies

```bash
pip install flask anthropic pdfplumber python-docx python-pptx pyttsx3 moviepy Pillow numpy
```

**Mac users:** pyttsx3 requires pyobjc:
```bash
pip install pyobjc
```

**Linux users:** pyttsx3 requires espeak:
```bash
sudo apt-get install espeak
```

### Step 2 — Set your API key

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Windows:**
```
set ANTHROPIC_API_KEY=sk-ant-...
```

### Step 3 — Run

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## How to use

1. Upload a PDF, DOCX, PPTX, or paste text into the sidebar
2. Type your topic focus (e.g. "health risks", "photosynthesis")
3. Pick **Whiteboard** or **Slides** style and a color theme
4. Click **Generate** — takes 30–90 seconds depending on document length
5. Watch the video in the browser, then download it as MP4

---

## Features

- **Two video styles:** Whiteboard (animated writing) and Slides (modern presentation)
- **Three themes:** Clean, Colorful, Dark
- **Text-to-speech narration** via pyttsx3 (offline, no API key needed)
- **Supported formats:** PDF, DOCX, PPTX, TXT, or plain pasted text
- **In-browser playback** with card-by-card navigation
- **MP4 download**

## File structure

```
chalkboard_ai/
├── app.py          # Flask backend
├── generator.py    # Claude API card generation
├── extractor.py    # File text extraction
├── renderer.py     # Frame rendering with Pillow
├── narrator.py     # Text-to-speech with pyttsx3
├── composer.py     # Stitch frames + audio into MP4
├── templates/
│   └── index.html  # Browser UI
├── static/
│   └── style.css   # App styles
└── requirements.txt
```

## Notes

- The app works fully offline except for the Anthropic API call and Google Fonts
- Temp files are stored in `<system temp>/chalkboard_ai/` and cleaned up on each new generation
- If pyttsx3 fails (e.g. no espeak on Linux), the video will still be generated silently
