"""Extract video URLs from YouTube channels and playlists."""

import re

import yt_dlp


def extract_video_urls(
    url: str, config: dict, max_videos: int = 0
) -> list[str]:
    """Extract individual video URLs from a channel/playlist/single video URL.

    Returns a list of video URLs.
    """
    # Single video URL — return as-is
    if _is_single_video(url):
        return [url]

    # Channel URL — append /videos to avoid shorts/live
    if _is_channel_url(url) and "/videos" not in url:
        url = url.rstrip("/") + "/videos"

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "ignoreerrors": True,
    }

    # Cookie handling
    if config.get("cookies_from_browser"):
        ydl_opts["cookiesfrombrowser"] = (config["cookies_from_browser"],)
    elif config.get("cookies_file"):
        ydl_opts["cookiefile"] = config["cookies_file"]

    if config.get("proxy"):
        ydl_opts["proxy"] = config["proxy"]

    urls = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info is None:
            return []

        if "entries" in info:
            for entry in info["entries"]:
                if entry is None:
                    continue
                video_id = entry.get("id", entry.get("url", ""))
                if video_id:
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    urls.append(video_url)
                if max_videos > 0 and len(urls) >= max_videos:
                    break
        else:
            video_id = info.get("id")
            if video_id:
                urls.append(f"https://www.youtube.com/watch?v={video_id}")

    return urls


def _is_single_video(url: str) -> bool:
    """Check if URL is a single video (not a playlist/channel)."""
    return bool(re.search(r"watch\?v=[\w-]+$", url)) or bool(
        re.search(r"youtu\.be/[\w-]+$", url)
    )


def _is_channel_url(url: str) -> bool:
    """Check if URL is a channel."""
    return bool(re.search(r"youtube\.com/(@[\w-]+|channel/[\w-]+)", url))
