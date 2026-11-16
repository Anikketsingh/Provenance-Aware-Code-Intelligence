"""The LLM behind explanations. Everything else depends only on the LLMBackend protocol."""

import os
from typing import Protocol

from dotenv import load_dotenv
from google import genai
from google.genai import types

from provenance.config import PROJECT_ROOT

#: Pinned for reproducibility. Results in the report must name the model that produced them.
DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"


class LLMBackend(Protocol):
    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int,
        temperature: float,
        seed: int,
        json_output: bool = False,
    ) -> str: ...


class MissingKeyError(RuntimeError):
    pass


class GeminiBackend:
    """Calls the Gemini API. Whatever is in the prompt leaves this machine."""

    def __init__(self, model: str | None = None):
        load_dotenv(PROJECT_ROOT / ".env")
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise MissingKeyError("Set GEMINI_API_KEY in .env (see .env.example).")
        self.model = model or os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        self._client = genai.Client(api_key=key)

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int,
        temperature: float,
        seed: int,
        json_output: bool = False,
    ) -> str:
        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            seed=seed,
            response_mime_type="application/json" if json_output else None,
        )
        response = self._client.models.generate_content(
            model=self.model, contents=prompt, config=config
        )
        return response.text or ""
