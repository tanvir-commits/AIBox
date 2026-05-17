"""HTTP client for a local Ollama server (/api/chat)."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings


class OllamaLLMProvider:
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self._base = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model
        self._timeout = settings.ollama_timeout_seconds

    def chat(self, *, system: str, user: str) -> str:
        with httpx.Client(timeout=self._timeout) as client:
            r = client.post(
                f"{self._base}/api/chat",
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "stream": False,
                },
            )
            r.raise_for_status()
            data = r.json()

        msg = data.get("message") if isinstance(data, dict) else None
        if isinstance(msg, dict):
            raw = msg.get("content") or ""
        else:
            raw = ""

        return str(raw).strip()

    def generate(self, prompt: str, stream: bool = False) -> str:
        """Satisfies LLMProvider; maps a bare prompt onto a minimal chat turn."""
        _ = stream
        return self.chat(
            system="You are a helpful assistant who answers succinctly.",
            user=prompt,
        )


def fetch_ollama_tags(settings: Settings) -> dict[str, Any]:
    """Raw JSON from Ollama `GET /api/tags` (installed models)."""
    base = settings.ollama_base_url.rstrip("/")
    with httpx.Client(timeout=15.0) as client:
        r = client.get(f"{base}/api/tags")
        r.raise_for_status()
        data = r.json()
    return data if isinstance(data, dict) else {}


def ping_ollama(settings: Settings) -> dict[str, str | bool]:
    """Cheap reachability probe for `/api/tags` — does not validate the configured model."""
    try:
        fetch_ollama_tags(settings)
        return {"ok": True, "detail": "reachable"}
    except (httpx.HTTPError, OSError, ValueError, TypeError) as exc:
        return {"ok": False, "detail": str(exc)}
