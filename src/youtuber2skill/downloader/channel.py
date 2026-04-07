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

    # Normalize playlist URL: watch?v=...&list=... -> playlist?list=...
    url = _normalize_playlist_url(url)

    # Channel URL — append /videos to avoid shorts/live
    if _is_channel_url(url) and "/videos" not in url:
        url = url.rstrip("/") + "/videos"

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "ignoreerrors": True,
    }
    _apply_common_opts(ydl_opts, config)

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


def _apply_common_opts(ydl_opts: dict, config: dict):
    """Apply cookie and proxy settings, gracefully handling failures."""
    cookies_browser = config.get("cookies_from_browser", "")
    cookies_file = config.get("cookies_file", "")

    if cookies_browser:
        try:
            # Test if browser cookies are accessible
            from yt_dlp.cookies import extract_cookies_from_browser
            extract_cookies_from_browser(cookies_browser)
            ydl_opts["cookiesfrombrowser"] = (cookies_browser,)
        except Exception:
            pass  # Browser cookies not accessible, proceed without
    elif cookies_file:
        from pathlib import Path
        if Path(cookies_file).exists():
            ydl_opts["cookiefile"] = cookies_file

    if config.get("proxy"):
        ydl_opts["proxy"] = config["proxy"]

    # Enable remote JS challenge solver for YouTube
    ydl_opts["remote_components"] = {"ejs": "github"}


def _is_single_video(url: str) -> bool:
    """Check if URL is a single video (not a playlist/channel)."""
    # URLs with list= parameter are playlists, not single videos
    if "list=" in url:
        return False
    return bool(re.search(r"watch\?v=[\w-]+", url)) or bool(
        re.search(r"youtu\.be/[\w-]+", url)
    )


def _normalize_playlist_url(url: str) -> str:
    """Convert watch?v=...&list=... to playlist?list=... for reliable extraction."""
    match = re.search(r"[?&]list=([\w-]+)", url)
    if match:
        return f"https://www.youtube.com/playlist?list={match.group(1)}"
    return url


def _is_channel_url(url: str) -> bool:
    """Check if URL is a channel."""
    return bool(re.search(r"youtube\.com/(@[\w-]+|channel/[\w-]+)", url))
