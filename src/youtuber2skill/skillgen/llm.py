"""Kimi K2.5 API client via OpenAI-compatible SDK."""

import time

from openai import OpenAI


class LLMClient:
    """Wrapper around Kimi K2.5 API."""

    MAX_RETRIES = 5
    RETRY_BASE_DELAY = 10  # seconds

    def __init__(self, config: dict):
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],
        )
        self.model = config.get("model", "kimi-k2.5")
        # kimi-k2.5 requires temperature=1 for thinking mode
        self.temperature = config.get("temperature", 1.0)

    def _call_with_retry(self, messages: list[dict]) -> str:
        """Call API with exponential backoff retry on rate limit errors."""
        for attempt in range(self.MAX_RETRIES):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                )
                return completion.choices[0].message.content
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower() or "overloaded" in str(e).lower():
                    delay = self.RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"  API rate limited, retrying in {delay}s (attempt {attempt + 1}/{self.MAX_RETRIES})...")
                    time.sleep(delay)
                else:
                    raise
        raise RuntimeError(f"API call failed after {self.MAX_RETRIES} retries")

    def chat(self, system_prompt: str, user_message: str) -> str:
        """Send a chat completion request and return the response text."""
        return self._call_with_retry([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ])

    def chat_with_messages(self, messages: list[dict]) -> str:
        """Send a multi-turn chat completion request."""
        return self._call_with_retry(messages)
