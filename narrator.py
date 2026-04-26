import os
import tempfile


def narrate_cards(cards: list[dict], tmp_dir: str) -> list[str] | None:
    try:
        import pyttsx3
    except ImportError:
        return None

    wav_paths = []
    for i, card in enumerate(cards):
        narration = card.get("narration", "").strip()
        if not narration:
            wav_paths.append(None)
            continue

        wav_path = os.path.join(tmp_dir, f"narration_{i}.wav")
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 1.0)
            engine.save_to_file(narration, wav_path)
            engine.runAndWait()
            engine.stop()

            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                wav_paths.append(wav_path)
            else:
                wav_paths.append(None)
        except Exception:
            wav_paths.append(None)

    if all(p is None for p in wav_paths):
        return None

    return wav_paths
