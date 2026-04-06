"""Kimi K2.5 API client via OpenAI-compatible SDK."""

from openai import OpenAI


class LLMClient:
    """Wrapper around Kimi K2.5 API."""

    def __init__(self, config: dict):
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],
        )
        self.model = config.get("model", "kimi-k2.5")
        self.temperature = config.get("temperature", 0.6)

    def chat(self, system_prompt: str, user_message: str) -> str:
        """Send a chat completion request and return the response text."""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=self.temperature,
        )
        return completion.choices[0].message.content

    def chat_with_messages(self, messages: list[dict]) -> str:
        """Send a multi-turn chat completion request."""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return completion.choices[0].message.content
