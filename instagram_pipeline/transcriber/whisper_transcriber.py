"""
whisper_transcriber.py
Extracts audio from video posts and transcribes them using OpenAI Whisper.
"""

import json
import os
import subprocess
import tempfile

import whisper
from tqdm import tqdm


def _find_video_file(post_dir: str, shortcode: str) -> str | None:
    """Return the path to a video file associated with *shortcode* inside *post_dir*."""
    for fname in os.listdir(post_dir):
        if shortcode in fname and fname.endswith(".mp4"):
            return os.path.join(post_dir, fname)
    # Fallback: return first .mp4 found in directory
    for fname in os.listdir(post_dir):
        if fname.endswith(".mp4"):
            return os.path.join(post_dir, fname)
    return None


def _extract_audio(video_path: str, audio_path: str) -> bool:
    """
    Extract the audio track from *video_path* and save as a WAV file to *audio_path*.

    Returns ``True`` on success, ``False`` otherwise.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                   # drop video stream
        "-acodec", "pcm_s16le",  # WAV format expected by Whisper
        "-ar", "16000",          # 16 kHz sample rate
        "-ac", "1",              # mono
        audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def transcribe_posts(output_dir: str, whisper_model_name: str = "base") -> None:
    """
    Read ``post_index.json``, transcribe all video posts with Whisper, and save
    one ``.txt`` file per post inside ``data/transcripts/``.

    Image posts receive an empty transcript file so that downstream steps can
    always assume the file exists.

    Args:
        output_dir:         Root data directory (e.g. ``"data"``).
        whisper_model_name: Whisper model size string (``"base"``, ``"small"``, …).
    """
    transcripts_dir = os.path.join(output_dir, "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)

    index_path = os.path.join(output_dir, "post_index.json")
    with open(index_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    print(f"[transcriber] Loading Whisper model '{whisper_model_name}' …")
    model = whisper.load_model(whisper_model_name)
    print("[transcriber] Model loaded.")

    for post in tqdm(posts, desc="Transcribing", unit="post"):
        shortcode = post["shortcode"]
        transcript_path = os.path.join(transcripts_dir, f"{shortcode}.txt")

        # Write empty transcript for image posts
        if not post.get("is_video"):
            if not os.path.exists(transcript_path):
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write("")
            continue

        # Skip if already transcribed
        if os.path.exists(transcript_path):
            continue

        video_path = _find_video_file(post.get("post_dir", ""), shortcode)
        if video_path is None:
            print(f"[transcriber] Warning: no video file found for {shortcode}")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write("")
            continue

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_path = tmp.name

        try:
            success = _extract_audio(video_path, audio_path)
            if not success:
                print(f"[transcriber] Warning: audio extraction failed for {shortcode}")
                transcript = ""
            else:
                result = model.transcribe(audio_path, fp16=False)
                transcript = result.get("text", "").strip()
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

    print(f"[transcriber] Transcripts saved to {transcripts_dir}")
