# youtuber2skill — Project Plan

## Overview

**youtuber2skill** is an open-source tool that automatically converts YouTube video content into structured AI Skills. It extracts knowledge and speaking style from YouTubers, generating skill files that AI assistants (like Claude Code) can use to answer questions as that YouTuber would.

**Pipeline**: YouTube Video → MP3 Audio → Text Transcript → Structured AI Skill

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        youtuber2skill                           │
│                                                                 │
│  ┌────────────┐   ┌─────────────┐   ┌───────────────────────┐  │
│  │  Stage 1   │   │   Stage 2   │   │       Stage 3         │  │
│  │ Video→Audio│──→│ Audio→Text  │──→│    Text→Skill         │  │
│  │            │   │             │   │                       │  │
│  │  yt-dlp    │   │ whisper.cpp │   │  Kimi K2.5 API        │  │
│  │  ffmpeg    │   │ (local)     │   │  (Prompt Pipeline)    │  │
│  └────────────┘   └─────────────┘   └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component         | Technology                          |
|-------------------|-------------------------------------|
| Language          | Python 3.12                         |
| Video Download    | yt-dlp + ffmpeg                     |
| Speech-to-Text   | pywhispercpp (whisper.cpp binding)  |
| Skill Generation  | Kimi K2.5 via OpenAI-compatible API |
| CLI Framework     | click                               |
| Config Format     | YAML                                |
| Skill Standard    | AgentSkills (agentskills.io)        |

## Project Structure

```
youtuber2skill/
├── pyproject.toml              # Project metadata & dependencies
├── README.md                   # Documentation
├── PLAN.md                     # This file
├── config.yaml                 # Default configuration
├── .gitignore
│
├── src/
│   └── youtuber2skill/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point (click)
│       ├── config.py           # Configuration management
│       ├── pipeline.py         # Orchestrates the 3-stage pipeline
│       │
│       ├── downloader/         # Stage 1: YouTube → Audio
│       │   ├── __init__.py
│       │   ├── channel.py      # Channel/playlist URL extraction
│       │   └── audio.py        # Video download & audio conversion
│       │
│       ├── transcriber/        # Stage 2: Audio → Text
│       │   ├── __init__.py
│       │   ├── whisper.py      # whisper.cpp integration
│       │   └── subtitle.py     # YouTube subtitle extraction (bypass whisper)
│       │
│       └── skillgen/           # Stage 3: Text → Skill
│           ├── __init__.py
│           ├── llm.py          # Kimi K2.5 API client
│           ├── analyzer.py     # Content & style analysis
│           ├── builder.py      # Skill file generation
│           └── prompts/        # Prompt templates
│               ├── intake.md
│               ├── knowledge_analyzer.md
│               ├── style_analyzer.md
│               ├── knowledge_builder.md
│               ├── style_builder.md
│               └── skill_merger.md
│
├── skills/                     # Generated skills output directory
│
└── tests/
    ├── test_downloader.py
    ├── test_transcriber.py
    └── test_skillgen.py
```

## Skill Output Format

Each generated skill follows the AgentSkills standard:

```
skills/{channel-slug}/
├── SKILL.md              # Entry point with YAML frontmatter
├── knowledge.md          # Extracted knowledge (topics, methods, opinions)
├── style.md              # Speaking style (catchphrases, tone, reasoning patterns)
├── meta.json             # Metadata (channel, video count, timestamps, version)
├── transcripts/          # Raw transcripts per video
│   ├── video_001.json
│   └── ...
└── versions/             # Version archive for rollback
```

## Stage Details

### Stage 1: YouTube → Audio

- Reuse patterns from the `../youtube/` (yt2mp3) project
- Use `yt-dlp` for downloading with cookie/proxy support
- Output 16kHz mono WAV for whisper.cpp consumption
- Extract YouTube subtitles when available (skip Stage 2)
- Save video metadata (title, description, upload date) to JSON
- Support channel/playlist batch processing with archive tracking

### Stage 2: Audio → Text

- Use `pywhispercpp` with `medium` or `large-v3-turbo` model
- Enable Silero-VAD for filtering silence/music
- Output timestamped JSON segments
- Skip transcription if YouTube subtitles were obtained in Stage 1
- Queue-based batch processing with resume support

### Stage 3: Text → Skill (Kimi K2.5)

Prompt pipeline inspired by colleague-skill:

1. **Knowledge Analyzer** — Extract topics, key arguments, methodologies, specific advice from transcripts
2. **Style Analyzer** — Extract speaking patterns, catchphrases, reasoning style, tone
3. **Knowledge Builder** — Organize analysis into structured knowledge.md
4. **Style Builder** — Generate style.md with concrete behavioral rules
5. **Skill Writer** — Assemble final SKILL.md with AgentSkills frontmatter

Design principles:
- Evidence-based: every knowledge point cites source video
- Specific: "recommends learning by building projects" not "good at teaching"
- Incremental: new videos merge into existing skill without full rebuild
- Layered: knowledge and style are independent, composable at runtime

### LLM Configuration (Kimi K2.5)

Uses OpenAI-compatible SDK. API key and base URL are loaded from `.env` file (never hardcoded).

```python
from openai import OpenAI

client = OpenAI(
    api_key=config["api_key"],    # from .env
    base_url=config["base_url"],  # from .env
)

completion = client.chat.completions.create(
    model="kimi-k2.5",
    messages=[...],
    temperature=0.6,  # instant mode
)
```

## Roadmap

### Phase 1 — MVP (Core Pipeline) ✦ Current Focus
- [x] Project scaffolding (pyproject.toml, directory structure, CLI)
- [ ] Stage 1: Single video download → WAV + metadata
- [ ] Stage 2: WAV → transcript via pywhispercpp
- [ ] Stage 3: Transcript → Skill via Kimi K2.5 prompt pipeline
- [ ] End-to-end: `youtuber2skill <youtube-url>` one-command flow

### Phase 2 — Batch & Quality
- [ ] Channel/playlist batch processing
- [ ] YouTube subtitle priority (skip transcription when available)
- [ ] Multi-video knowledge merging (incremental skill update)
- [ ] Progress persistence & resume
- [ ] Skill quality scoring

### Phase 3 — Experience & Ecosystem
- [ ] Claude Code skill integration (`/{channel-slug}` invocation)
- [ ] Web UI (progress visualization, skill preview/edit)
- [ ] Skill sharing (export/import)
- [ ] Multi-language optimization
- [ ] Docker deployment

## CLI Interface Design

```bash
# Single video → skill
youtuber2skill run https://www.youtube.com/watch?v=xxx

# Entire channel
youtuber2skill run https://www.youtube.com/@ChannelName --max-videos 50

# Individual stages
youtuber2skill download https://www.youtube.com/watch?v=xxx -o ./audio/
youtuber2skill transcribe ./audio/video.wav -o ./transcripts/
youtuber2skill generate ./transcripts/ -o ./skills/

# Configuration
youtuber2skill config --show
youtuber2skill config --set whisper.model large-v3-turbo
```

## Configuration (config.yaml)

```yaml
downloader:
  cookies_from_browser: safari
  quality: 128
  threads: 3
  proxy: ""

transcriber:
  model: medium
  language: auto
  vad: true
  threads: 6

skillgen:
  model: kimi-k2.5
  temperature: 0.6
  # api_key and base_url loaded from .env

output:
  skills_dir: ./skills
  keep_audio: false
  keep_transcripts: true
```
