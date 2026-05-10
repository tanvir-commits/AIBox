"""Deterministic mock LLM for CPU-only development and tests."""

from __future__ import annotations


class MockLLMProvider:
    name = "mock_llm"

    def generate(self, prompt: str, stream: bool = False) -> str:
        _ = stream
        lowered = prompt.lower()
        if "not found" in lowered or "no context" in lowered:
            return (
                "I could not find that in the indexed company documents."
            )
        if "emergency" in lowered and "office manager" in lowered:
            return (
                "Staff must notify the office manager within 15 minutes."
            )
        return "This is a mock_llm response. Configure Ollama in a later phase."
