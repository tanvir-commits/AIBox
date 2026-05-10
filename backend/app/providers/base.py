from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, prompt: str, stream: bool = False) -> str: ...


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...
