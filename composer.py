import os

FPS = 24


def compose_video(frame_paths: list, cards: list, audio_paths, output_path: str) -> str:
    """Compose JPEG frame files + MP3 audio files into an MP4.
    Deletes frame files after export. Exports silently if audio fails."""
    try:
        from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips
        _v2 = False
    except ImportError:
        from moviepy import ImageSequenceClip, AudioFileClip, concatenate_audioclips
        _v2 = True

    video_clip = ImageSequenceClip(frame_paths, fps=FPS)

    audio_clip = None
    if audio_paths and any(p is not None for p in audio_paths):
        segments = []
        for ap in audio_paths:
            if ap and os.path.exists(ap) and os.path.getsize(ap) > 0:
                try:
                    segments.append(AudioFileClip(ap))
                except Exception:
                    pass

        if segments:
            try:
                audio_clip = concatenate_audioclips(segments)
            except Exception:
                audio_clip = None

    if audio_clip is not None:
        if _v2:
            video_clip = video_clip.with_audio(audio_clip)
        else:
            video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(output_path, codec="libx264",
                                   audio_codec="aac", logger=None)
    else:
        video_clip.write_videofile(output_path, codec="libx264", logger=None)

    # Delete frame files — use set() since hold frames share a path
    for p in set(frame_paths):
        try:
            os.remove(p)
        except OSError:
            pass

    return output_path
