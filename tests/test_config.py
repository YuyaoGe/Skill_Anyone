"""Tests for configuration management."""

import os
import tempfile

from youtuber2skill.config import load_config, _deep_merge


def test_deep_merge():
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"b": {"c": 99}, "e": 5}
    result = _deep_merge(base, override)
    assert result == {"a": 1, "b": {"c": 99, "d": 3}, "e": 5}


def test_load_default_config():
    config = load_config("/nonexistent/path.yaml")
    assert config["skillgen"]["model"] == "kimi-k2.5"
    assert config["skillgen"]["base_url"] == ""
    assert config["transcriber"]["model"] == "medium"


def test_env_override():
    os.environ["KIMI_API_KEY"] = "test-key-123"
    try:
        config = load_config("/nonexistent/path.yaml")
        assert config["skillgen"]["api_key"] == "test-key-123"
    finally:
        del os.environ["KIMI_API_KEY"]


def test_load_yaml_config():
    yaml_content = """
skillgen:
  model: kimi-k2.5
  temperature: 0.8
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config = load_config(f.name)
        assert config["skillgen"]["temperature"] == 0.8
        assert config["skillgen"]["model"] == "kimi-k2.5"
        # Default values preserved
        assert config["downloader"]["threads"] == 3
    os.unlink(f.name)
