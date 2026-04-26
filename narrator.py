import os


def narrate_cards(cards: list, tmp_dir: str):
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
            # Fresh engine per card avoids state bleed across platforms
            engine = pyttsx3.init()
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 1.0)

            # On Windows, pick a clear SAPI5 voice if available
            voices = engine.getProperty("voices")
            if voices:
                # Prefer English voice
                en_voice = next(
                    (v for v in voices if "english" in (v.name or "").lower() or "en" in (v.id or "").lower()),
                    voices[0],
                )
                engine.setProperty("voice", en_voice.id)

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
