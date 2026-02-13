"""
Unified LLM client — supports Anthropic, OpenAI, and Google.

Routes to the right provider based on model name.
"""

import os
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified interface for multiple LLM providers."""

    def __init__(self):
        self._clients = {}
        self._init_providers()

    def _init_providers(self):
        """Initialize available providers based on API keys."""
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                import anthropic
                self._clients["anthropic"] = anthropic.AsyncAnthropic()
                logger.info("Anthropic client initialized")
            except ImportError:
                logger.warning("anthropic package not installed")

        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                self._clients["openai"] = openai.AsyncOpenAI()
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("openai package not installed")

        if os.getenv("GOOGLE_API_KEY"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self._clients["google"] = genai
                logger.info("Google client initialized")
            except ImportError:
                logger.warning("google-generativeai package not installed")

    def _get_provider(self, model: str) -> str:
        """Determine provider from model name."""
        if "claude" in model or "anthropic" in model:
            return "anthropic"
        elif "gpt" in model or "o1" in model:
            return "openai"
        elif "gemini" in model:
            return "google"
        raise ValueError(f"Unknown model provider for: {model}")

    async def chat(
        self,
        model: str,
        system: str,
        message: str,
        tools: Optional[list] = None,
    ) -> str:
        """Send a message to the LLM and get a response."""
        provider = self._get_provider(model)

        if provider not in self._clients:
            raise RuntimeError(
                f"Provider '{provider}' not available. "
                f"Set the appropriate API key in .env"
            )

        if provider == "anthropic":
            return await self._chat_anthropic(model, system, message)
        elif provider == "openai":
            return await self._chat_openai(model, system, message)
        elif provider == "google":
            return await self._chat_google(model, system, message)

    async def _chat_anthropic(self, model: str, system: str, message: str) -> str:
        client = self._clients["anthropic"]
        response = await client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": message}],
        )
        return response.content[0].text

    async def _chat_openai(self, model: str, system: str, message: str) -> str:
        client = self._clients["openai"]
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
        )
        return response.choices[0].message.content

    async def _chat_google(self, model: str, system: str, message: str) -> str:
        genai = self._clients["google"]
        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system,
        )
        response = await asyncio.to_thread(
            gen_model.generate_content, message
        )
        return response.text
