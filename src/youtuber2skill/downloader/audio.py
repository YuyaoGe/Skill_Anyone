"""Download YouTube videos and extract audio."""

import json
from pathlib import Path

import yt_dlp

from .channel import extract_video_urls


def download_audio(
    url: str,
    output_dir: str,
    config: dict,
    max_videos: int = 0,
) -> list[dict]:
    """Download audio from YouTube URL(s).

    Returns list of dicts with keys: audio_path, video_id, title, url, metadata.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    video_urls = extract_video_urls(url, config, max_videos=max_videos)
    results = []

    for video_url in video_urls:
        result = _download_single(video_url, output_path, config)
        if result:
            results.append(result)

    return results


def _download_single(url: str, output_dir: Path, config: dict) -> dict | None:
    """Download a single video as WAV audio + metadata."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "postprocessor_args": [
            "-ar", "16000",   # 16kHz for whisper
            "-ac", "1",       # mono
        ],
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "writesubtitles": True,
        "subtitleslangs": ["zh-Hans", "zh", "en"],
        "subtitlesformat": "vtt",
    }

    if config.get("cookies_from_browser"):
        ydl_opts["cookiesfrombrowser"] = (config["cookies_from_browser"],)
    elif config.get("cookies_file"):
        ydl_opts["cookiefile"] = config["cookies_file"]

    if config.get("proxy"):
        ydl_opts["proxy"] = config["proxy"]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                return None

            video_id = info["id"]
            audio_path = output_dir / f"{video_id}.wav"

            metadata = {
                "video_id": video_id,
                "title": info.get("title", ""),
                "channel": info.get("channel", info.get("uploader", "")),
                "upload_date": info.get("upload_date", ""),
                "description": info.get("description", ""),
                "duration": info.get("duration", 0),
                "url": url,
            }

            # Save metadata alongside audio
            meta_path = output_dir / f"{video_id}.meta.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            return {
                "audio_path": str(audio_path),
                "video_id": video_id,
                "title": metadata["title"],
                "url": url,
                "metadata": metadata,
            }

    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return None
