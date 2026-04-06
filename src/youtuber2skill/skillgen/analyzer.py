"""Analyze transcripts to extract knowledge and style patterns."""

import json
from pathlib import Path

from .llm import LLMClient


PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_file = PROMPTS_DIR / f"{name}.md"
    return prompt_file.read_text(encoding="utf-8")


def analyze_knowledge(transcripts: list[dict], llm: LLMClient) -> str:
    """Analyze transcripts to extract knowledge, topics, and methodologies.

    Processes transcripts in chunks to handle token limits.
    """
    system_prompt = _load_prompt("knowledge_analyzer")

    # Prepare transcript text, chunked if needed
    all_text = _prepare_transcript_text(transcripts)

    results = []
    for chunk in _chunk_text(all_text, max_chars=60000):
        user_message = f"以下是视频转录文本，请分析并提取知识体系：\n\n{chunk}"
        result = llm.chat(system_prompt, user_message)
        results.append(result)

    if len(results) == 1:
        return results[0]

    # Merge multiple chunk analyses
    merge_prompt = (
        "你之前分析了同一YouTuber的多段视频内容。"
        "请将以下多次分析结果合并为一份完整的知识体系分析：\n\n"
    )
    for i, r in enumerate(results, 1):
        merge_prompt += f"--- 分析 {i} ---\n{r}\n\n"

    return llm.chat(system_prompt, merge_prompt)


def analyze_style(transcripts: list[dict], llm: LLMClient) -> str:
    """Analyze transcripts to extract speaking style and personality patterns."""
    system_prompt = _load_prompt("style_analyzer")

    all_text = _prepare_transcript_text(transcripts)

    results = []
    for chunk in _chunk_text(all_text, max_chars=60000):
        user_message = f"以下是视频转录文本，请分析表达风格：\n\n{chunk}"
        result = llm.chat(system_prompt, user_message)
        results.append(result)

    if len(results) == 1:
        return results[0]

    merge_prompt = (
        "请将以下多次风格分析结果合并为一份完整的风格分析：\n\n"
    )
    for i, r in enumerate(results, 1):
        merge_prompt += f"--- 分析 {i} ---\n{r}\n\n"

    return llm.chat(system_prompt, merge_prompt)


def _prepare_transcript_text(transcripts: list[dict]) -> str:
    """Prepare transcript text with video titles as headers."""
    parts = []
    for t in transcripts:
        title = t.get("title", t.get("video_id", "Unknown"))
        text = t.get("text", "")
        if text:
            parts.append(f"## {title}\n\n{text}")
    return "\n\n---\n\n".join(parts)


def _chunk_text(text: str, max_chars: int = 60000) -> list[str]:
    """Split text into chunks, respecting section boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    sections = text.split("\n\n---\n\n")
    current_chunk = ""

    for section in sections:
        if len(current_chunk) + len(section) > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = section
        else:
            if current_chunk:
                current_chunk += "\n\n---\n\n" + section
            else:
                current_chunk = section

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
