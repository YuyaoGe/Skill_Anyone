"""Download and parse YouTube subtitles as an alternative to whisper transcription."""

import re

import yt_dlp

from ..downloader.channel import _apply_common_opts


def download_subtitles(url: str, config: dict) -> str | None:
    """Try to download YouTube subtitles for a video.

    Returns subtitle text if available, None otherwise.
    """
    if not url:
        return None

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["zh-Hans", "zh", "en"],
        "subtitlesformat": "vtt",
    }
    _apply_common_opts(ydl_opts, config)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return None

            # Check for manual subtitles first, then auto-generated
            for sub_source in ("subtitles", "automatic_captions"):
                subs = info.get(sub_source, {})
                for lang in ["zh-Hans", "zh", "en"]:
                    if lang in subs:
                        # Get the VTT format URL
                        for fmt in subs[lang]:
                            if fmt.get("ext") == "vtt":
                                vtt_url = fmt["url"]
                                return _fetch_and_parse_vtt(vtt_url, ydl)

    except Exception:
        pass

    return None


def _fetch_and_parse_vtt(vtt_url: str, ydl: yt_dlp.YoutubeDL) -> str | None:
    """Fetch VTT content and parse to plain text."""
    try:
        vtt_content = ydl.urlopen(vtt_url).read().decode("utf-8")
        return _parse_vtt(vtt_content)
    except Exception:
        return None


def _parse_vtt(vtt_content: str) -> str:
    """Parse VTT subtitle content to plain text, removing duplicates."""
    lines = []
    seen = set()

    for line in vtt_content.split("\n"):
        line = line.strip()
        # Skip headers, timestamps, empty lines
        if not line or line.startswith("WEBVTT") or line.startswith("NOTE"):
            continue
        if re.match(r"\d{2}:\d{2}", line):
            continue
        if "-->" in line:
            continue

        # Remove VTT tags
        clean = re.sub(r"<[^>]+>", "", line)
        clean = clean.strip()

        if clean and clean not in seen:
            seen.add(clean)
            lines.append(clean)

    return " ".join(lines) if lines else ""
