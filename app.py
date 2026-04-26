import os
import shutil
import tempfile
import traceback

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)

# Global state for the latest generated video
_state = {"video_path": None, "cards": []}

TEMP_DIR = os.path.join(tempfile.gettempdir(), "chalkboard_ai")


def _ensure_tmp():
    os.makedirs(TEMP_DIR, exist_ok=True)


def _cleanup_tmp():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    os.makedirs(TEMP_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    from extractor import extract_from_file, extract_text
    from generator import generate_cards
    from renderer import render_frames
    from narrator import narrate_cards
    from composer import compose_video

    _cleanup_tmp()

    try:
        topic = request.form.get("topic", "").strip()
        style = request.form.get("style", "Whiteboard")
        theme = request.form.get("theme", "Clean")
        pasted_text = request.form.get("text", "").strip()

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # Extract text
        content = ""
        uploaded_file = request.files.get("file")
        if uploaded_file and uploaded_file.filename:
            tmp_upload = os.path.join(TEMP_DIR, "upload_" + uploaded_file.filename)
            uploaded_file.save(tmp_upload)
            content = extract_from_file(tmp_upload, uploaded_file.filename)
        elif pasted_text:
            content = extract_text(pasted_text)

        if not content:
            return jsonify({"error": "No content provided — upload a file or paste text"}), 400

        # Generate cards via Claude
        cards = generate_cards(content, topic)

        # Render frames — writes JPEGs to TEMP_DIR, returns file paths
        frames = render_frames(cards, style, theme, TEMP_DIR)

        # Narrate
        wav_paths = narrate_cards(cards, TEMP_DIR)

        # Compose video
        video_path = os.path.join(TEMP_DIR, "output.mp4")
        compose_video(frames, cards, wav_paths, video_path)

        _state["video_path"] = video_path
        _state["cards"] = cards

        return jsonify({"success": True, "cards": cards})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/video")
def video():
    video_path = _state.get("video_path")
    if not video_path or not os.path.exists(video_path):
        return "Video not found", 404
    return send_file(video_path, mimetype="video/mp4")


@app.route("/download")
def download():
    video_path = _state.get("video_path")
    if not video_path or not os.path.exists(video_path):
        return "Video not found", 404
    return send_file(
        video_path,
        mimetype="video/mp4",
        as_attachment=True,
        download_name="chalkboard_video.mp4",
    )


if __name__ == "__main__":
    _ensure_tmp()
    app.run(debug=True, host="0.0.0.0", port=5000)
