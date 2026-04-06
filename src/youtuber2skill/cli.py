"""CLI entry point for youtuber2skill."""

import click

from . import __version__
from .config import load_config
from .pipeline import run_pipeline


@click.group()
@click.version_option(version=__version__)
@click.option("--config", "-c", default=None, help="Path to config file")
@click.pass_context
def main(ctx, config):
    """Convert YouTube videos into structured AI Skills."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)


@main.command()
@click.argument("url")
@click.option("--max-videos", "-n", default=0, help="Max videos to process (0=all)")
@click.option("--output", "-o", default=None, help="Output directory for skills")
@click.pass_context
def run(ctx, url, max_videos, output):
    """Run the full pipeline: download → transcribe → generate skill."""
    config = ctx.obj["config"]
    if output:
        config["output"]["skills_dir"] = output

    click.echo(f"Processing: {url}")
    run_pipeline(url, config, max_videos=max_videos)


@main.command()
@click.argument("url")
@click.option("--output", "-o", default="./audio", help="Output directory")
@click.option("--max-videos", "-n", default=0, help="Max videos (0=all)")
@click.pass_context
def download(ctx, url, output, max_videos):
    """Download YouTube video(s) as audio."""
    from .downloader.audio import download_audio

    config = ctx.obj["config"]
    results = download_audio(url, output, config["downloader"], max_videos=max_videos)
    click.echo(f"Downloaded {len(results)} file(s) to {output}")


@main.command()
@click.argument("audio_path")
@click.option("--output", "-o", default="./transcripts", help="Output directory")
@click.pass_context
def transcribe(ctx, audio_path, output):
    """Transcribe audio file(s) to text."""
    from .transcriber.whisper import transcribe_audio

    config = ctx.obj["config"]
    result = transcribe_audio(audio_path, output, config["transcriber"])
    click.echo(f"Transcription saved to {result}")


@main.command()
@click.argument("transcript_dir")
@click.option("--output", "-o", default=None, help="Output directory for skill")
@click.pass_context
def generate(ctx, transcript_dir, output):
    """Generate AI skill from transcripts."""
    from .skillgen.builder import build_skill

    config = ctx.obj["config"]
    if output:
        config["output"]["skills_dir"] = output
    skill_path = build_skill(transcript_dir, config)
    click.echo(f"Skill generated at {skill_path}")


if __name__ == "__main__":
    main()
