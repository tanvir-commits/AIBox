"""Local ONNX sentence embeddings via FastEmbed (no PyTorch dependency)."""

from __future__ import annotations

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

_model_lock = threading.Lock()
_models: dict[str, Any] = {}


class FastEmbedEmbeddingProvider:
    name = "fastembed"

    def __init__(self, model_name: str, *, dimensions: int) -> None:
        self.model_name = model_name
        self.dimensions = dimensions

    def _model(self):  # type: ignore[no-untyped-def]
        with _model_lock:
            if self.model_name not in _models:
                try:
                    from fastembed import TextEmbedding  # noqa: PLC0415
                except ImportError as exc:  # pragma: no cover
                    raise ImportError(
                        "fastembed is not installed. Install backend dev deps: pip install -e \".[dev]\"",
                    ) from exc
                logger.info(
                    "loading embedding model %s (dim=%s, first embed may download weights)",
                    self.model_name,
                    self.dimensions,
                )
                _models[self.model_name] = TextEmbedding(model_name=self.model_name)
            return _models[self.model_name]

    def embed(self, text: str) -> list[float]:
        stripped = text.strip() or "."
        model = self._model()
        vec = next(iter(model.embed([stripped])))
        return vec.astype(float).tolist()[: self.dimensions]
