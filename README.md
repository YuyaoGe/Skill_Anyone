# youtuber2skill

Convert YouTube videos into structured AI Skills. Extract knowledge and speaking style from any YouTuber, generating skill files that AI assistants can use to answer questions as that YouTuber would.

## Pipeline

```
YouTube Video → MP3 Audio → Text Transcript → Structured AI Skill
```

## Quick Start

```bash
# Install
pip install -e .

# Run full pipeline (single video)
youtuber2skill run https://www.youtube.com/watch?v=xxx

# Run full pipeline (entire channel, last 50 videos)
youtuber2skill run https://www.youtube.com/@ChannelName --max-videos 50
```

## Individual Stages

```bash
# Stage 1: Download audio
youtuber2skill download https://www.youtube.com/watch?v=xxx -o ./audio/

# Stage 2: Transcribe audio
youtuber2skill transcribe ./audio/video.wav -o ./transcripts/

# Stage 3: Generate skill
youtuber2skill generate ./transcripts/ -o ./skills/
```

## Configuration

Copy `config.yaml` and customize:

```yaml
downloader:
  cookies_from_browser: safari    # or chrome, firefox, etc.
  quality: 128
  threads: 3

transcriber:
  model: medium                   # tiny, base, small, medium, large-v3-turbo
  language: auto
  vad: true

skillgen:
  model: kimi-k2.5
  # api_key and base_url are loaded from .env file

output:
  skills_dir: ./skills
  keep_transcripts: true
```

Set credentials via `.env` file:

```bash
cp .env.example .env
# Then edit .env with your KIMI_API_KEY and KIMI_BASE_URL
```

## Skill Output

Generated skills follow the [AgentSkills](https://agentskills.io) standard:

```
skills/{channel-slug}/
├── SKILL.md              # Entry point
├── knowledge.md          # Extracted knowledge base
├── style.md              # Speaking style rules
├── meta.json             # Metadata
└── transcripts/          # Source transcripts
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Video Download | yt-dlp + ffmpeg |
| Speech-to-Text | whisper.cpp (via pywhispercpp) |
| Skill Generation | Kimi K2.5 (OpenAI-compatible API) |
| CLI | click |

## Requirements

- Python 3.10+
- ffmpeg (install via `brew install ffmpeg` on macOS)
- yt-dlp
- whisper.cpp model files (auto-downloaded by pywhispercpp)

## License

MIT
