"""Build skill files from analysis results."""

import json
from datetime import datetime
from pathlib import Path

from .llm import LLMClient
from .analyzer import analyze_knowledge, analyze_style, _load_prompt


def build_skill(transcript_dir: str, config: dict) -> str:
    """Build a complete skill from transcripts.

    Returns path to the generated skill directory.
    """
    transcript_path = Path(transcript_dir)
    transcripts = _load_transcripts(transcript_path)

    if not transcripts:
        raise ValueError(f"No transcripts found in {transcript_dir}")

    llm = LLMClient(config["skillgen"])

    # Determine channel name / slug
    channel_name = _detect_channel_name(transcripts)
    slug = _slugify(channel_name)

    skills_dir = Path(config["output"]["skills_dir"])
    skill_dir = skills_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Save transcripts if configured
    if config["output"].get("keep_transcripts", True):
        t_dir = skill_dir / "transcripts"
        t_dir.mkdir(exist_ok=True)
        for t in transcripts:
            vid = t.get("video_id", "unknown")
            with open(t_dir / f"{vid}.json", "w", encoding="utf-8") as f:
                json.dump(t, f, ensure_ascii=False, indent=2)

    # Parallel analysis: knowledge + style
    print("  Analyzing knowledge...")
    knowledge_analysis = analyze_knowledge(transcripts, llm)

    print("  Analyzing style...")
    style_analysis = analyze_style(transcripts, llm)

    # Build final documents
    print("  Building knowledge document...")
    knowledge_doc = _build_knowledge(knowledge_analysis, llm)

    print("  Building style document...")
    style_doc = _build_style(style_analysis, llm)

    # Write skill files
    _write_skill_md(skill_dir, slug, channel_name)
    _write_file(skill_dir / "knowledge.md", knowledge_doc)
    _write_file(skill_dir / "style.md", style_doc)
    _write_meta(skill_dir, slug, channel_name, transcripts)

    return str(skill_dir)


def _load_transcripts(transcript_dir: Path) -> list[dict]:
    """Load all transcript JSON files from directory."""
    transcripts = []
    for f in sorted(transcript_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            transcripts.append(json.load(fh))
    return transcripts


def _detect_channel_name(transcripts: list[dict]) -> str:
    """Detect channel name from transcript metadata."""
    for t in transcripts:
        meta = t.get("metadata", {})
        channel = meta.get("channel", "")
        if channel:
            return channel
    # Fallback to first title
    if transcripts:
        return transcripts[0].get("title", "unknown-channel")
    return "unknown-channel"


def _slugify(name: str) -> str:
    """Convert a name to a filesystem-friendly slug."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug or "unknown"


def _build_knowledge(analysis: str, llm: LLMClient) -> str:
    """Build the knowledge.md document from analysis."""
    system_prompt = _load_prompt("knowledge_builder")
    user_message = f"基于以下知识分析结果，生成结构化的knowledge.md文档：\n\n{analysis}"
    return llm.chat(system_prompt, user_message)


def _build_style(analysis: str, llm: LLMClient) -> str:
    """Build the style.md document from analysis."""
    system_prompt = _load_prompt("style_builder")
    user_message = f"基于以下风格分析结果，生成结构化的style.md文档：\n\n{analysis}"
    return llm.chat(system_prompt, user_message)


def _write_skill_md(skill_dir: Path, slug: str, channel_name: str):
    """Write the SKILL.md entry point."""
    content = f"""---
name: {slug}
description: "AI Skill generated from {channel_name}'s YouTube content"
user-invocable: true
---

# {channel_name} Skill

This skill replicates the knowledge and communication style of **{channel_name}** based on their YouTube video content.

## How it works

When invoked, this skill:
1. **PART A (Knowledge)**: Applies the extracted knowledge base from `knowledge.md` to answer the user's question
2. **PART B (Style)**: Delivers the response in {channel_name}'s characteristic style from `style.md`

## Usage

Invoke this skill with a question or topic, and the AI will respond as {channel_name} would — using their knowledge, reasoning patterns, and communication style.

## Rules

- Always ground responses in the knowledge base; do not fabricate information beyond what was extracted
- Maintain the speaking style consistently
- When the knowledge base doesn't cover a topic, acknowledge the gap honestly in {channel_name}'s voice
"""
    _write_file(skill_dir / "SKILL.md", content)


def _write_meta(
    skill_dir: Path, slug: str, channel_name: str, transcripts: list[dict]
):
    """Write meta.json with skill metadata."""
    meta = {
        "name": channel_name,
        "slug": slug,
        "version": 1,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "video_count": len(transcripts),
        "videos": [
            {
                "video_id": t.get("video_id", ""),
                "title": t.get("title", ""),
            }
            for t in transcripts
        ],
    }
    with open(skill_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def _write_file(path: Path, content: str):
    """Write content to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
