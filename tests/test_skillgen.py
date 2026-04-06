"""Tests for the skill generation module."""

from youtuber2skill.skillgen.builder import _slugify
from youtuber2skill.skillgen.analyzer import _chunk_text, _prepare_transcript_text


def test_slugify():
    assert _slugify("My Channel Name") == "my-channel-name"
    assert _slugify("  Spaces  ") == "spaces"
    assert _slugify("special!@#chars") == "specialchars"
    assert _slugify("") == "unknown"


def test_chunk_text_short():
    text = "Short text"
    chunks = _chunk_text(text, max_chars=1000)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_long():
    sections = ["Section " + str(i) + " " * 100 for i in range(20)]
    text = "\n\n---\n\n".join(sections)
    chunks = _chunk_text(text, max_chars=500)
    assert len(chunks) > 1


def test_prepare_transcript_text():
    transcripts = [
        {"title": "Video 1", "text": "Hello world"},
        {"title": "Video 2", "text": "Foo bar"},
    ]
    result = _prepare_transcript_text(transcripts)
    assert "## Video 1" in result
    assert "Hello world" in result
    assert "## Video 2" in result
    assert "Foo bar" in result
