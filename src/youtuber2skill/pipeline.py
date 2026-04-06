"""Main pipeline orchestrating the 3 stages."""

import json
from pathlib import Path

import click

from .downloader.audio import download_audio
from .downloader.channel import extract_video_urls
from .transcriber.whisper import transcribe_audio
from .transcriber.subtitle import download_subtitles
from .skillgen.builder import build_skill


def run_pipeline(url: str, config: dict, max_videos: int = 0):
    """Run the full youtuber2skill pipeline.

    Stage 1: Download audio from YouTube
    Stage 2: Transcribe audio to text
    Stage 3: Generate AI skill from transcripts
    """
    skills_dir = Path(config["output"]["skills_dir"])
    work_dir = skills_dir / ".work"
    audio_dir = work_dir / "audio"
    transcript_dir = work_dir / "transcripts"
    audio_dir.mkdir(parents=True, exist_ok=True)
    transcript_dir.mkdir(parents=True, exist_ok=True)

    # --- Stage 1: Download ---
    click.echo("\n[Stage 1/3] Downloading audio...")

    video_urls = extract_video_urls(url, config["downloader"], max_videos=max_videos)
    click.echo(f"  Found {len(video_urls)} video(s)")

    audio_files = download_audio(
        url, str(audio_dir), config["downloader"], max_videos=max_videos
    )
    click.echo(f"  Downloaded {len(audio_files)} audio file(s)")

    # --- Stage 2: Transcribe ---
    click.echo("\n[Stage 2/3] Transcribing audio...")

    for audio_info in audio_files:
        audio_path = audio_info["audio_path"]
        video_id = audio_info.get("video_id", Path(audio_path).stem)

        # Try YouTube subtitles first
        subtitle_text = download_subtitles(
            audio_info.get("url", ""), config["downloader"]
        )

        if subtitle_text:
            click.echo(f"  Using YouTube subtitles for: {audio_info.get('title', video_id)}")
            transcript_path = transcript_dir / f"{video_id}.json"
            transcript_data = {
                "video_id": video_id,
                "title": audio_info.get("title", ""),
                "source": "youtube_subtitle",
                "text": subtitle_text,
                "segments": [],
            }
            with open(transcript_path, "w", encoding="utf-8") as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
        else:
            click.echo(f"  Transcribing: {audio_info.get('title', video_id)}")
            transcribe_audio(audio_path, str(transcript_dir), config["transcriber"])

    # --- Stage 3: Generate Skill ---
    click.echo("\n[Stage 3/3] Generating skill...")

    skill_path = build_skill(str(transcript_dir), config)
    click.echo(f"\nSkill generated at: {skill_path}")

    # Cleanup
    if not config["output"].get("keep_audio", False):
        import shutil
        shutil.rmtree(audio_dir, ignore_errors=True)

    return skill_path
