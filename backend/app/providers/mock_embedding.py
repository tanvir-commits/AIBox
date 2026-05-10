"""Deterministic mock embeddings from text (CPU-only, no model)."""

from __future__ import annotations

import hashlib
import struct


class MockEmbeddingProvider:
    name = "mock_embedding"
    dimensions: int = 384

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        floats: list[float] = []
        for i in range(0, len(digest), 4):
            chunk = digest[i : i + 4].ljust(4, b"\0")
            (u32,) = struct.unpack(">I", chunk)
            floats.append((u32 % 10000) / 10000.0)
        while len(floats) < self.dimensions:
            digest = hashlib.sha256(digest).digest()
            for j in range(0, len(digest), 4):
                if len(floats) >= self.dimensions:
                    break
                chunk = digest[j : j + 4].ljust(4, b"\0")
                (u32,) = struct.unpack(">I", chunk)
                floats.append((u32 % 10000) / 10000.0)
        return floats[: self.dimensions]
