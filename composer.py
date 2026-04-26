import os
import numpy as np

FPS = 24


def compose_video(frame_paths: list, cards: list, audio_paths, output_path: str) -> str:
    """Accept a list of JPEG file paths (or .wav/.mp3). Deletes frame files after export."""
    try:
        import moviepy.editor as mpy
        _v2 = False
    except ImportError:
        import moviepy as mpy
        _v2 = True

    # ImageSequenceClip reads files on demand — no numpy array needed
    video_clip = mpy.ImageSequenceClip(frame_paths, fps=FPS)

    audio_clip = None
    if audio_paths and any(p is not None for p in audio_paths):
        audio_segments = []
        for i, (card, ap) in enumerate(zip(cards, audio_paths)):
            if ap and os.path.exists(ap) and os.path.getsize(ap) > 0:
                try:
                    audio_segments.append(mpy.AudioFileClip(ap))
                except Exception:
                    audio_segments.append(None)
            else:
                audio_segments.append(None)

            # 0.4s silence between cards to match hold frames
            if i < len(cards) - 1:
                try:
                    if _v2:
                        silence = mpy.AudioArrayClip(np.zeros((int(44100 * 0.4), 2)), fps=44100)
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
        video_clip.write_videofile(output_path, codec="libx264",
                                   audio_codec="aac", logger=None)
    else:
        video_clip.write_videofile(output_path, codec="libx264", logger=None)

    # Delete frame files — keep only unique paths (hold frames share a path)
    for p in set(frame_paths):
        try:
            os.remove(p)
        except OSError:
            pass

    return output_path
