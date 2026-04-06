"""Configuration management."""

import os
from pathlib import Path

import yaml


DEFAULT_CONFIG = {
    "downloader": {
        "cookies_from_browser": "safari",
        "quality": 128,
        "threads": 3,
        "proxy": "",
    },
    "transcriber": {
        "model": "medium",
        "language": "auto",
        "vad": True,
        "threads": 6,
    },
    "skillgen": {
        "api_key": "",
        "base_url": "",
        "model": "kimi-k2.5",
        "temperature": 0.6,
    },
    "output": {
        "skills_dir": "./skills",
        "keep_audio": False,
        "keep_transcripts": True,
    },
}


def load_config(config_path: str | None = None) -> dict:
    """Load config from YAML file, falling back to defaults."""
    config = DEFAULT_CONFIG.copy()

    # Load .env file if present
    _load_dotenv()

    if config_path is None:
        config_path = os.environ.get("YOUTUBER2SKILL_CONFIG", "config.yaml")

    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            user_config = yaml.safe_load(f) or {}
        config = _deep_merge(config, user_config)

    # Environment variable overrides
    env_api_key = os.environ.get("KIMI_API_KEY")
    if env_api_key:
        config["skillgen"]["api_key"] = env_api_key

    env_base_url = os.environ.get("KIMI_BASE_URL")
    if env_base_url:
        config["skillgen"]["base_url"] = env_base_url

    return config


def _load_dotenv():
    """Load .env file from current directory if it exists."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = value


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dicts, override takes precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
