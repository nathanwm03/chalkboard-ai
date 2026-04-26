import os
import base64
import requests


GOOGLE_TTS_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"


def narrate_cards(cards: list, tmp_dir: str):
    api_key = os.environ.get("GOOGLE_TTS_KEY", "").strip()
    if not api_key:
        return None

    mp3_paths = []
    for i, card in enumerate(cards):
        narration = card.get("narration", "").strip()
        if not narration:
            mp3_paths.append(None)
            continue

        mp3_path = os.path.join(tmp_dir, f"narration_{i}.mp3")
        try:
            payload = {
                "input": {"text": narration},
                "voice": {
                    "languageCode": "en-US",
                    "name": "en-US-Neural2-D",
                    "ssmlGender": "MALE",
                },
                "audioConfig": {"audioEncoding": "MP3"},
            }
            resp = requests.post(
                GOOGLE_TTS_URL,
                params={"key": api_key},
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            audio_bytes = base64.b64decode(resp.json()["audioContent"])
            with open(mp3_path, "wb") as f:
                f.write(audio_bytes)

            if os.path.getsize(mp3_path) > 0:
                mp3_paths.append(mp3_path)
            else:
                mp3_paths.append(None)
        except Exception:
            mp3_paths.append(None)

    if all(p is None for p in mp3_paths):
        return None

    return mp3_paths
