"""Download YouTube videos and extract audio."""

import json
import queue
import threading
from pathlib import Path

import yt_dlp

from .channel import extract_video_urls, _apply_common_opts

_print_lock = threading.Lock()


def download_audio(
    url: str,
    output_dir: str,
    config: dict,
    max_videos: int = 0,
) -> list[dict]:
    """Download audio from YouTube URL(s).

    Returns list of dicts with keys: audio_path, video_id, title, url, metadata.
    Uses multi-threaded downloading when threads > 1 in config.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    video_urls = extract_video_urls(url, config, max_videos=max_videos)
    num_threads = min(config.get("threads", 3), len(video_urls))

    if num_threads <= 1:
        # Sequential fallback
        results = []
        for i, video_url in enumerate(video_urls, 1):
            with _print_lock:
                print(f"  [{i}/{len(video_urls)}] Downloading: {video_url}")
            result = _download_single(video_url, output_path, config)
            if result:
                results.append(result)
        return results

    # Multi-threaded download
    url_q = queue.Queue()
    for i, video_url in enumerate(video_urls, 1):
        url_q.put((i, video_url))

    total = len(video_urls)
    results = []
    results_lock = threading.Lock()
    completed = [0]

    def worker():
        """Each worker thread owns a persistent yt-dlp instance."""
        while True:
            try:
                i, video_url = url_q.get_nowait()
            except queue.Empty:
                break

            with _print_lock:
                print(f"  [{i}/{total}] Downloading: {video_url}")

            result = _download_single(video_url, output_path, config)

            with results_lock:
                if result:
                    results.append(result)
                completed[0] += 1

            with _print_lock:
                print(f"  [{completed[0]}/{total}] Completed: {result['title'] if result else 'failed'}")

            url_q.task_done()

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return results


def _download_single(url: str, output_dir: Path, config: dict) -> dict | None:
    """Download a single video as WAV audio + metadata."""
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
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
        "no_warnings": False,
        "ignoreerrors": True,
        "writesubtitles": True,
        "subtitleslangs": ["zh-Hans", "zh", "en"],
        "subtitlesformat": "vtt",
    }
    _apply_common_opts(ydl_opts, config)

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
