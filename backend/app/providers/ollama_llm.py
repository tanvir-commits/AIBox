"""HTTP client for a local Ollama server (/api/chat)."""

from __future__ import annotations

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


def ping_ollama(settings: Settings) -> dict[str, str | bool]:
    """Cheap reachability probe for `/api/tags` — does not validate the configured model."""
    base = settings.ollama_base_url.rstrip("/")
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(f"{base}/api/tags")
            r.raise_for_status()
        return {"ok": True, "detail": "reachable"}
    except (httpx.HTTPError, OSError) as exc:
        return {"ok": False, "detail": str(exc)}
