import os
import numpy as np
from PIL import Image

FPS = 24


def compose_video(frames: list, cards: list, wav_paths, output_path: str) -> str:
    # moviepy v2 removed moviepy.editor; fall back gracefully
    try:
        import moviepy.editor as mpy
        _v2 = False
    except ImportError:
        import moviepy as mpy
        _v2 = True

    np_frames = [np.array(f.convert("RGB")) for f in frames]
    video_clip = mpy.ImageSequenceClip(np_frames, fps=FPS)

    audio_clip = None
    if wav_paths and any(p is not None for p in wav_paths):
        audio_segments = []
        for i, (card, wav_path) in enumerate(zip(cards, wav_paths)):
            if wav_path and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                try:
                    audio_segments.append(mpy.AudioFileClip(wav_path))
                except Exception:
                    audio_segments.append(None)
            else:
                audio_segments.append(None)

            # 0.4s silence between cards to match hold frames
            if i < len(cards) - 1:
                try:
                    if _v2:
                        silence_arr = np.zeros((int(44100 * 0.4), 2))
                        silence = mpy.AudioArrayClip(silence_arr, fps=44100)
                    else:
                        silence = mpy.AudioClip(lambda t: 0, duration=0.4, fps=44100)
                    audio_segments.append(silence)
                except Exception:
                    pass

        valid = [s for s in audio_segments if s is not None]
        if valid:
            try:
                audio_clip = mpy.concatenate_audioclips(valid)
            except Exception:
                audio_clip = None

    if audio_clip is not None:
        vid_dur = video_clip.duration
        if audio_clip.duration > vid_dur:
            audio_clip = audio_clip.subclip(0, vid_dur)

        if _v2:
            video_clip = video_clip.with_audio(audio_clip)
        else:
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
