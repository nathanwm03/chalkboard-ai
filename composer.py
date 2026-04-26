import os
import numpy as np
from PIL import Image

FPS = 24
HOLD_FRAMES = int(0.4 * FPS)


def compose_video(frames: list[Image.Image], cards: list[dict], wav_paths: list[str] | None, output_path: str) -> str:
    import moviepy.editor as mpy

    # Convert PIL frames to numpy arrays
    np_frames = [np.array(f.convert("RGB")) for f in frames]

    video_clip = mpy.ImageSequenceClip(np_frames, fps=FPS)

    audio_clip = None
    if wav_paths and any(p is not None for p in wav_paths):
        audio_segments = []
        for i, (card, wav_path) in enumerate(zip(cards, wav_paths)):
            if wav_path and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                try:
                    card_audio = mpy.AudioFileClip(wav_path)
                    audio_segments.append(card_audio)
                except Exception:
                    audio_segments.append(None)
            else:
                audio_segments.append(None)

            # Add 0.4s silence between cards
            if i < len(cards) - 1:
                silence = mpy.AudioClip(lambda t: 0, duration=0.4, fps=44100)
                audio_segments.append(silence)

        valid_segments = [s for s in audio_segments if s is not None]
        if valid_segments:
            try:
                audio_clip = mpy.concatenate_audioclips(valid_segments)
            except Exception:
                audio_clip = None

    if audio_clip is not None:
        # Trim or pad audio to match video duration
        video_duration = video_clip.duration
        if audio_clip.duration > video_duration:
            audio_clip = audio_clip.subclip(0, video_duration)

        video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger=None,
            verbose=False,
        )
    else:
        video_clip.write_videofile(
            output_path,
            codec="libx264",
            logger=None,
            verbose=False,
        )

    return output_path
